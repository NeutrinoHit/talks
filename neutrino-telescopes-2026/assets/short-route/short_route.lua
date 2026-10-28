-- Short route: keep only the sections, slides and tabs listed under `short-route:` in the document metadata.
-- The full lecture stays the single source of the content; a slide or tab is selected by its slide id
-- (`## Title {#id}`) and by the text of its tab heading (`### Title`); the tabs come in the order of the list.
-- Everything else is dropped.
-- `drop-classes` removes every div with one of the listed classes (for example a passage kept only in the full lecture).
-- A slide entry with `replace: file.qmd` is swapped for the slide in that file (a layout used only in the short route).
-- A slide entry with `after: file.qmd` gets the slide(s) of that file right behind it (a slide used only in the short route).
-- A slide entry with `append: [{file: f.qmd, tab: Name}]` adds the blocks of the file at the end of the slide or of that tab.
-- A listed id or tab that no longer exists stops the render, so edits of the full lecture cannot go unnoticed.

local text = pandoc.utils.stringify

local function read_blocks(path)
  local f = assert(io.open(path, 'r'), 'short-route: cannot open ' .. path)
  local doc = pandoc.read(f:read('a'), 'markdown')
  f:close()
  return doc.blocks
end

local function read_route(meta)
  local route = meta['short-route']
  if not route then error('short-route: metadata missing') end
  local sections, slides, order = {}, {}, {}
  for _, id in ipairs(route.sections or {}) do sections[text(id)] = true end
  for _, item in ipairs(route.slides or {}) do
    local id, tabs = text(item.id), nil
    if item.tabs then
      tabs = { order = {}, used = {} }
      for _, t in ipairs(item.tabs) do
        tabs.order[#tabs.order + 1] = text(t)
        tabs.used[text(t)] = false
      end
    end
    slides[id] = { tabs = tabs, replace = item.replace and text(item.replace) or nil, after = item.after and text(item.after) or nil,
                    append = {} }
    for _, a in ipairs(item.append or {}) do
      slides[id].append[#slides[id].append + 1] = { file = text(a.file), tab = a.tab and text(a.tab) or nil }
    end
    order[#order + 1] = id
  end
  local drop = {}
  for _, c in ipairs(route['drop-classes'] or {}) do drop[text(c)] = true end
  return sections, slides, order, drop
end

-- inside one tabset: keep the listed tabs, in the order of the list
local function filter_tabset(div, tabs, slide_id, tab_blocks)
  local before, groups, current = {}, {}, nil
  for _, b in ipairs(div.content) do
    if b.t == 'Header' and b.level == 3 then
      current = {}
      groups[text(b.content)] = current
    end
    if current then current[#current + 1] = b else before[#before + 1] = b end
  end
  local out = before
  for _, name in ipairs(tabs.order) do
    if groups[name] then
      tabs.used[name] = true
      for _, b in ipairs(groups[name]) do out[#out + 1] = b end
      for _, extra in ipairs(tab_blocks and tab_blocks[name] or {}) do out[#out + 1] = extra end
    end
  end
  div.content = out
  return div
end

function Pandoc(doc)
  local sections, slides, order, drop = read_route(doc.meta)
  local seen_sections, out = {}, {}
  local keep, tabs, slide_id = true, nil, nil
  local pending = nil     -- slides to put behind the current slide (`after:`)
  local tail = nil        -- blocks to put at the end of the current slide (`append:` without a tab)
  local tab_blocks = nil  -- blocks to put at the end of a tab (`append:` with a tab)
  local function flush()
    if tail then
      for _, rb in ipairs(tail) do out[#out + 1] = rb end
      tail = nil
    end
    if pending then
      for _, rb in ipairs(pending) do out[#out + 1] = rb end
      pending = nil
    end
  end
  for _, b in ipairs(doc.blocks) do
    if b.t == 'Header' and b.level <= 2 then flush() end
    if b.t == 'Header' and b.level == 1 then
      keep, tabs, slide_id = sections[b.identifier] == true, nil, nil
      if keep then seen_sections[b.identifier] = true end
    elseif b.t == 'Header' and b.level == 2 then
      local s = slides[b.identifier]
      keep, tabs, slide_id = s ~= nil, s and s.tabs, b.identifier
      if s then
        s.found = true
        if s.after then pending = read_blocks(s.after) end
        tail, tab_blocks = nil, nil
        for _, a in ipairs(s.append) do
          if a.tab then
            tab_blocks = tab_blocks or {}
            tab_blocks[a.tab] = tab_blocks[a.tab] or {}
            for _, rb in ipairs(read_blocks(a.file)) do table.insert(tab_blocks[a.tab], rb) end
          else
            tail = tail or {}
            for _, rb in ipairs(read_blocks(a.file)) do tail[#tail + 1] = rb end
          end
        end
        if s.replace then
          for _, rb in ipairs(read_blocks(s.replace)) do out[#out + 1] = rb end
          keep = false
        end
      end
    end
    if keep then
      if tabs and b.t == 'Div' and b.classes:includes('panel-tabset') then
        b = filter_tabset(b, tabs, slide_id, tab_blocks)
      end
      out[#out + 1] = pandoc.walk_block(b, { Div = function(d)
        for _, c in ipairs(d.classes) do if drop[c] then return {} end end
      end })
    end
  end
  flush()
  for id in pairs(sections) do
    if not seen_sections[id] then error('short-route: no section ' .. id) end
  end
  for _, id in ipairs(order) do
    local s = slides[id]
    if not s.found then error('short-route: no slide ' .. id) end
    for name, used in pairs(s.tabs and s.tabs.used or {}) do
      if not used then error('short-route: slide ' .. id .. ' has no tab "' .. name .. '"') end
    end
  end
  doc.blocks = out
  return doc
end

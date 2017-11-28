alias rg="rg -S -p --column --colors 'path:fg:yellow' --colors 'path:style:bold' --colors 'line:style:bold' --colors 'match:style:intense'"
rgvi () {
    rg --vimgrep --no-heading $* | vim -
}


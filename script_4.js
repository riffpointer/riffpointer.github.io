
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            gfm: true,
            breaks: true,
            highlight: function(code, lang) {
                if (typeof hljs !== 'undefined') {
                    if (lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (__) {}
                    }
                    return hljs.highlightAuto(code).value;
                }
                return code;
            }
        });
    }
    
    function parseSimpleMarkdown(md) {
        let html = md;
        // Escape HTML
        html = html.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        // Headers
        html = html.replace(/^# (.*)$/gm, "<h1>$1</h1>");
        html = html.replace(/^## (.*)$/gm, "<h2>$1</h2>");
        html = html.replace(/^### (.*)$/gm, "<h3>$1</h3>");
        html = html.replace(/^#### (.*)$/gm, "<h4>$1</h4>");
        html = html.replace(/^##### (.*)$/gm, "<h5>$1</h5>");
        html = html.replace(/^###### (.*)$/gm, "<h6>$1</h6>");
        // Bold / Italic
        html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
        // Inline code
        html = html.replace(/`(.*?)`/g, "<code>$1</code>");
        // Code blocks
        html = html.replace(/```(.*?)\n([\s\S]*?)```/g, "<pre><code>$2</code></pre>");
        // Links
        html = html.replace(/\[(.*?)\]\((.*?)\)/g, "<a href='$2'>$1</a>");
        // Paragraphs / Newlines
        html = html.replace(/\n/g, "<br>");
        return html;
    }
    
    function updatePreview(md) {
        if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
            document.getElementById('content').innerHTML = marked.parse(md);
        } else {
            document.getElementById('content').innerHTML = parseSimpleMarkdown(md);
        }
        if (window.renderMathInElement) {
            renderMathInElement(document.getElementById('content'), {
                delimiters: [
                    {left: '$$', right: '$$', display: true},
                    {left: '$', right: '$', display: false},
                    {left: '\(', right: '\)', display: false},
                    {left: '\[', right: '\]', display: true}
                ],
                throwOnError: false
            });
        }
    }
    
    function setTheme(themeName) {
        document.body.className = themeName;
        // Switch highlight.js theme based on markdown theme dark/light mode
        let hljsTheme = document.getElementById('hljs-theme');
        if (themeName.includes('dark') || themeName === 'dracula' || themeName === 'monokai') {
            hljsTheme.href = "https://cdn.jsdelivr.net/npm/highlight.js@11.8.0/styles/github-dark.min.css";
        } else {
            hljsTheme.href = "https://cdn.jsdelivr.net/npm/highlight.js@11.8.0/styles/github.min.css";
        }
    }
  
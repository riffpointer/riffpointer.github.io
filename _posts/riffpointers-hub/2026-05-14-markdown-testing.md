---
layout: post
title: "Markdown Testing"
date: 2026-05-14 10:00:00 +05:30
categories: [markdown, testing, reference]
tags: [markdown, latex, code]
description: A reference post for testing Markdown, LaTeX, code, and rich content rendering.
usemathjax: true
---

This post is a compact test page for common Markdown features, LaTeX rendering, syntax highlighting, and mixed HTML content.

# Heading 1

## Heading 2

### Heading 3

#### Heading 4

##### Heading 5

###### Heading 6

## Paragraphs and inline formatting

This is a paragraph with **bold text**, *italic text*, ***bold italic text***, ~~strikethrough text~~, `inline code`, and a keyboard shortcut: <kbd>Ctrl</kbd> + <kbd>K</kbd>.

Markdown can also include links like [Jekyll](https://jekyllrb.com), automatic URLs like <https://example.com>, and email links like <hello@example.com>.

Use inline HTML when needed: <mark>highlighted text</mark>, <sup>superscript</sup>, <sub>subscript</sub>, and <abbr title="HyperText Markup Language">HTML</abbr>.

## Blockquotes

> This is a blockquote.
>
> It can span multiple paragraphs and include **formatting**.
>
> > Nested blockquotes should also render clearly.

## Lists

### Unordered list

- First item
- Second item
  - Nested item
  - Another nested item
- Third item

### Ordered list

1. First step
2. Second step
   1. Nested step
   2. Another nested step
3. Third step

### Task list

- [x] Render headings
- [x] Render lists
- [ ] Confirm every edge case manually

### Definition list

Markdown
: A lightweight markup language.

Kramdown
: The Markdown parser commonly used by Jekyll.

## Tables

| Feature | Markdown | Notes |
| --- | ---: | --- |
| Bold | `**text**` | Strong emphasis |
| Italic | `*text*` | Emphasis |
| Code | `` `text` `` | Inline code |
| Table | Pipes | Alignment supported |

## Code

Inline code looks like `const answer = 42`.

```javascript
function fibonacci(n) {
  if (n < 2) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

console.log(fibonacci(8));
```

```python
from dataclasses import dataclass

@dataclass
class Post:
    title: str
    published: bool = True

post = Post("Markdown Testing")
print(post)
```

```ruby
class MarkdownTest
  def initialize(title)
    @title = title
  end

  def publish
    puts "Publishing #{@title}"
  end
end
```

```css
.markdown-test {
  display: grid;
  gap: 1rem;
  color: #eaeaea;
}
```

```html
<article class="markdown-test">
  <h2>Rendered HTML</h2>
  <p>This block is escaped inside a code fence.</p>
</article>
```

```bash
bundle exec jekyll build
```

## LaTeX

Inline math should render inside text, such as \\(E = mc^2\\), \\(a^2 + b^2 = c^2\\), and \\(\sum_{i=1}^{n} i = \frac{n(n+1)}{2}\\).

Block math:

<div>
\\[
\int_{-\infty}^{\infty} e^{-x^2}\,dx = \sqrt{\pi}
\\]
</div>

Aligned equations:

<div>
\\[
\begin{aligned}
\nabla \cdot \mathbf{E} &= \frac{\rho}{\varepsilon_0} \\
\nabla \cdot \mathbf{B} &= 0 \\
\nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}}{\partial t} \\
\nabla \times \mathbf{B} &= \mu_0 \mathbf{J} + \mu_0\varepsilon_0\frac{\partial \mathbf{E}}{\partial t}
\end{aligned}
\\]
</div>

Matrix notation:

<div>
\\[
A =
\begin{bmatrix}
1 & 2 & 3 \\
4 & 5 & 6 \\
7 & 8 & 9
\end{bmatrix}
\\]
</div>

## Images

![RiffPointer avatar](/assets/img/avatar.jpg)

Image with a title:

![RiffPointer avatar](/assets/img/avatar.jpg "RiffPointer avatar")

## Horizontal rule

---

## Footnotes

Here is a sentence with a footnote.[^note]

[^note]: This is the footnote content. It can include **Markdown formatting**.

## Escaping characters

Use backslashes to escape Markdown syntax: \*not italic\*, \`not code\`, and \[not a link\].

## HTML details

<details>
  <summary>Expandable section</summary>
  <p>This content is written in raw HTML inside Markdown.</p>
</details>

## Mixed content

> A quote with a list:
>
> 1. One
> 2. Two
> 3. Three

And a final paragraph after all test content.

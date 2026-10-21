export default (root) => {
    // Read the actual published article, excluding literal examples in code blocks.
    const texts = [];
    for (const e of root.querySelectorAll('p,div,li')) {
        if (!e.closest('pre,code,script,style') && !e.querySelector('p,div,li,pre,code')) {
            texts.push(e.textContent);
        }
    }
    const headings = Array.from(root.querySelectorAll('h1,h2,h3,h4,h5,h6'));
    return {
        headings: headings.map(e => Number(e.tagName.slice(1))),
        codeBlocks: root.querySelectorAll('pre').length,
        tables: Array.from(root.querySelectorAll('table')).map(e => e.querySelectorAll('tr').length),
        listItems: root.querySelectorAll('li').length,
        anchors: Array.from(root.querySelectorAll('a[name]')).map(e => e.name),
        links: Array.from(root.querySelectorAll('a[href]')).map(e => e.getAttribute('href')),
        rawMarkdown: texts.filter(s => /\|\s*:?-{3,}|\[[^\]\n]+\]\([^)]+\)/.test(s)).slice(0, 20),
        rawHeadingClasses: headings.filter(e => /\{\.[^}]+\}/.test(e.textContent)).map(e => e.textContent),
        codeImages: Array.from(root.querySelectorAll('code img')).map(e => e.alt),
        containers: Array.from(root.querySelectorAll('.overflow-auto,.content-list,.collection-method-list,.code-list-no-flex-break,#valet-support')).map(e => ({
            class: e.className, tables: e.querySelectorAll('table').length,
            links: e.querySelectorAll('a').length, listItems: e.querySelectorAll('li').length
        }))
    };
};

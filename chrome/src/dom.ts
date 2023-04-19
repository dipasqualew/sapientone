
const FORM_ELEMENTS = ['input', 'select', 'textarea'];

export const getElementUniqueId = (element: HTMLElement): string => {
    const components = []

    components.push(element.tagName.toLowerCase());

    if (element.id) {
        components.push(`#${element.id}`);
    }

    if (element.className) {
        components.push(`.${element.className.split(' ').join('.')}`);
    }

    return components.join('');
};

export const findContainingForms = (element: HTMLElement): HTMLElement[] => {
    let parent = element.parentElement;
    const found = new Map<string, HTMLElement>();

    while (parent && parent !== document.body) {
        const results: string[] = [];
        parent.querySelectorAll(FORM_ELEMENTS.join(',')).forEach((item) => results.push(getElementUniqueId(item as HTMLElement)));

        if (results.length) {
            const key = results.join('-');
            if (!found.has(key)) {
                found.set(key, parent);
            }
        }

        parent = parent.parentElement;
    }

    return [...found.values()]
};

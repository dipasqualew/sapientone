import { ref } from 'vue';

import { setupApp } from './app';
import { getStorage, getContextMenu } from "./di";
import { AnswerQuestionResponse, QuerySapientoneLike, QuerySapientoneKey } from './injectionKeys'
import { findContainingForms } from './dom';
import Query from './components/Query.vue';

export const question = ref<string>('');
export const answer = ref<string>('');


export const querySapientone = async (text: string): Promise<AnswerQuestionResponse> => {
    const storage = getStorage();
    const appSettings = await storage.get(["SAPIENTONE_API_KEY", "SAPIENTONE_URL"]);

    const headers = {
        "Content-Type": "application/json",
        "Authorization": appSettings.SAPIENTONE_API_KEY || "",
    }
    const result = await fetch(appSettings.SAPIENTONE_URL || "", {
        headers,
        method: "POST",
        body: JSON.stringify({ question: text }),
    });

    return await result.json();
};

export const createLabel = (target: HTMLElement, text: string, identifier: string): void => {
    if (!target.parentNode) {
        return;
    }

    const label = document.createElement('div');
    label.dataset.identifier = identifier;
    label.style.position = 'absolute';
    label.style.padding = '5px 10px';
    label.style.backgroundColor = 'white';
    label.style.border = '1px solid #ccc';
    label.style.cursor = 'pointer';
    label.style.zIndex = '10';
    label.style.userSelect = 'none';

    label.innerText = text;

    const targetRect = target.getBoundingClientRect();
    label.style.left = `${targetRect.left + targetRect.width + 10}px`;
    label.style.top = `${targetRect.top + window.scrollY}px`;


    target.parentNode.insertBefore(label, target);

    label.addEventListener('mouseenter', () => {
        const inputs = target.querySelectorAll('input, textarea, select') as NodeListOf<HTMLInputElement>;
        inputs.forEach((input) => input.style.border = '1px solid red')
    });

    label.addEventListener('mouseleave', () => {
        const inputs = target.querySelectorAll('input, textarea, select') as NodeListOf<HTMLInputElement>;
        inputs.forEach((input) => input.style.border = '');
    })

    label.addEventListener('click', () => {
        target.removeChild(label)
        target.style.border = '';
    });
};
export const init = (QuerySapientone: QuerySapientoneLike): void => {
    const root = document.createElement('div')
    root.id = 'sapientone-query-root'
    document.body.appendChild(root)

    const dependencies = [
        {
            symbol: QuerySapientoneKey,
            value: QuerySapientone,
        },
    ];

    const app = setupApp(Query, '#sapientone-query-root', dependencies);

    document.addEventListener("keydown", async (event: KeyboardEvent): Promise<void> => {
        if (event.ctrlKey && event.key === "b") {
            event.preventDefault();
            const selection = window.getSelection();

            if (!selection) {
                return;
            }

            question.value = selection.toString();
        }
    });

    const contextMenu = getContextMenu();

    contextMenu.create({
        title: 'Ask Sapientone',
        onclick: async (info, tab) => {
            const forms = findContainingForms(document.activeElement as HTMLElement);

            forms.forEach((form) => {
                createLabel(form, 'Sapientone', 'sapientone')
            })
        },
    })
}

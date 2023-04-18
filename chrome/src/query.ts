import { ref } from 'vue';

import { setupApp } from './app';
import { getStorage } from "./di";
import { AnswerQuestionResponse, QuerySapientoneLike, QuerySapientoneKey } from './injectionKeys'
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
}

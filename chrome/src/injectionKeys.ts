import type { InjectionKey } from 'vue';


export interface AnswerQuestionResponse {
    question: string;
    answer: string;
}

export type QuerySapientoneLike = (text: string) => Promise<AnswerQuestionResponse>

export const QuerySapientoneKey = Symbol() as InjectionKey<QuerySapientoneLike>;

import { AnswerQuestionResponse } from '../../injectionKeys';
import { init } from '../../query';

const QUESTIONS_AND_ANSWERS: Record<string, string> = {
    "What is my name?": "William Di Pasquale",
    "Where do I live?": "Sheffield, UK",
};

const mockedQuerySapientone = async (question: string): Promise<AnswerQuestionResponse> => {
    const answer = QUESTIONS_AND_ANSWERS[question.trim()] || "I don't know";

    return {
        question,
        answer,
    }
};

init(mockedQuerySapientone);

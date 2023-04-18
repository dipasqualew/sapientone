<script setup lang="ts">
import { computed, inject } from 'vue'
import { QuerySapientoneKey } from '../injectionKeys';
import { question, answer, querySapientone } from '../query';

const showDialog = computed(() => !!question.value);

const query = inject(QuerySapientoneKey, querySapientone);

const onQueryClick = async () => {
    if (!question.value) {
        return;
    }

    const response = await query(question.value);
    answer.value = response.answer
}

const closeDialog = () => {
    question.value = '';
    answer.value = '';
};
</script>
<template>
    <v-dialog :model-value="showDialog" :update:modelValue="closeDialog" width="800">
        <v-card>
            <v-card-text>
                <div>
                    <v-textarea label="Question" v-model="question" />
                </div>
                <div>
                    <v-textarea label="Answer" v-model="answer" />
                </div>
            </v-card-text>
            <v-card-actions>
                <v-btn v-if="question && !answer" color="primary" @click="onQueryClick">Query</v-btn>
                <v-btn color="danger" block @click="closeDialog">Close Dialog</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

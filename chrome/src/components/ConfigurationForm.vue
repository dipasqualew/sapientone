<script setup lang="ts">
import { useAppSettings } from '../hooks';

const appSettings = useAppSettings();
</script>

<template>
    <div class="form">
        <div class="input">
            <v-text-field label="Sapientone URL" variant="outlined" v-model="appSettings.SAPIENTONE_URL" />
        </div>
        <div class="input">
            <v-text-field label="Sapientone API Key" variant="outlined" v-model="appSettings.SAPIENTONE_API_KEY" />
        </div>
    </div>
</template>

<style>
.form {
    min-width: 400px;
    padding: 15px;
}

.input {
    margin-bottom: 1rem;
}
</style>

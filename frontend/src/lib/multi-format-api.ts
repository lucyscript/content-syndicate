import api from './api';

export interface MultiFormatRequest {
  source_content: string | any[];
  topic?: string;
  target_audience?: string;
  tone?: string;
  selected_formats?: string[];
  custom_instructions?: string;
}

export interface SingleFormatRequest {
  source_content: string | any[];
  format_name: string;
  topic?: string;
  target_audience?: string;
  tone?: string;
  custom_instructions?: string;
}

export interface RepurposeRequest {
  source_format: string;
  target_formats: string[];
  content: string;
  preserve_core_message?: boolean;
}

export const multiFormatAPI = {
  generateMultiFormat: async (data: MultiFormatRequest) => {
    return api.post('/api/multi-format/generate-multi-format', data);
  },

  generateSingleFormat: async (data: SingleFormatRequest) => {
    return api.post('/api/multi-format/generate-single-format', data);
  },

  repurposeContent: async (data: RepurposeRequest) => {
    return api.post('/api/multi-format/repurpose-content', data);
  },

  getSupportedFormats: async () => {
    return api.get('/api/multi-format/supported-formats');
  },

  getGenerationHistory: async (limit = 20, offset = 0) => {
    return api.get(`/api/multi-format/generation-history?limit=${limit}&offset=${offset}`);
  },

  getGenerationDetails: async (generationId: number) => {
    return api.get(`/api/multi-format/generation/${generationId}`);
  },

  validateContent: async (content: string, formatName: string) => {
    return api.post('/api/multi-format/validate-content', {
      content,
      format_name: formatName
    });
  },

  getFormatTemplates: async () => {
    return api.get('/api/multi-format/format-templates');
  }
};

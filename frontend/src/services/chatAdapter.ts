import type { AnswerCitationResponse } from './api';
import { askCourseQuestion } from './api';
import type { ChatResponse, ChatService, Citation } from '../types/chat';


const COURSE_ID = import.meta.env.VITE_COURSE_ID as string | undefined;


function formatPageLabel(citation: AnswerCitationResponse): string {
  if (citation.page_start === citation.page_end) {
    return `p. ${citation.page_start}`;
  }
  return `pp. ${citation.page_start}–${citation.page_end}`;
}


function mapCitation(citation: AnswerCitationResponse): Citation {
  return {
    id: citation.chunk_id,
    label: `${citation.document_title} · ${formatPageLabel(citation)}`,
    documentId: citation.document_id,
    pageStart: citation.page_start,
    pageEnd: citation.page_end,
  };
}


export const courseChatService: ChatService = {
  async sendMessage(prompt: string, signal?: AbortSignal): Promise<ChatResponse> {
    if (!COURSE_ID) {
      throw new Error('VITE_COURSE_ID is not configured.');
    }

    const response = await askCourseQuestion(COURSE_ID, prompt, signal);
    return {
      content: response.answer,
      citations: response.citations.map(mapCitation),
    };
  },
};

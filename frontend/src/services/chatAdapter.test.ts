import { afterEach, describe, expect, it, vi } from 'vitest';
import { courseChatService } from './chatAdapter';


describe('courseChatService', () => {
  afterEach(() => vi.restoreAllMocks());

  it('maps a grounded backend answer and its page citation', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          answer: 'The Addition Rule prevents overlap from being counted twice.',
          citations: [
            {
              chunk_id: 'chunk-1',
              document_id: 'document-1',
              document_title: 'math-180a-ch2',
              page_start: 2,
              page_end: 2,
            },
          ],
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    );
    vi.stubGlobal('fetch', fetchMock);

    const response = await courseChatService.sendMessage('Explain the Addition Rule.');

    expect(response).toEqual({
      content: 'The Addition Rule prevents overlap from being counted twice.',
      citations: [
        {
          id: 'chunk-1',
          label: 'math-180a-ch2 · p. 2',
          documentId: 'document-1',
          pageStart: 2,
          pageEnd: 2,
        },
      ],
    });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/courses\/[^/]+\/ask$/),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ question: 'Explain the Addition Rule.' }),
      }),
    );
  });
});

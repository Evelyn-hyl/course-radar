import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { ChatComposer } from './ChatComposer';

describe('ChatComposer', () => {
  it('rejects whitespace and submits a trimmed prompt with Enter', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn<() => Promise<void>>().mockResolvedValue();
    render(
      <ChatComposer selectedPrompt={null} isPending={false} onSubmit={onSubmit} onSelectionApplied={() => undefined} />,
    );

    const input = screen.getByRole('textbox', { name: 'Course question' });
    await user.type(input, '   ');
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled();

    await user.clear(input);
    await user.type(input, '  Explain Hamiltonian cycles{enter}');
    expect(onSubmit).toHaveBeenCalledWith('Explain Hamiltonian cycles');
  });

  it('keeps a newline when Shift+Enter is pressed', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn<() => Promise<void>>().mockResolvedValue();
    render(
      <ChatComposer selectedPrompt={null} isPending={false} onSubmit={onSubmit} onSelectionApplied={() => undefined} />,
    );

    const input = screen.getByRole('textbox', { name: 'Course question' });
    await user.type(input, 'First line{shift>}{enter}{/shift}Second line');
    expect(input).toHaveValue('First line\nSecond line');
    expect(onSubmit).not.toHaveBeenCalled();
  });
});

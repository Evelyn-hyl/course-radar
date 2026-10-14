import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { App } from './App';

describe('App', () => {
  afterEach(() => vi.restoreAllMocks());

  it('populates the composer from a suggestion without submitting it', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole('button', { name: /Hamiltonian cycles explained/i }));
    expect(screen.getByRole('textbox', { name: 'Course question' })).toHaveValue(
      'How are Hamiltonian cycles explained in lectures vs in the textbook?',
    );
    expect(screen.queryByText('M0 preview')).not.toBeInTheDocument();
  });
});

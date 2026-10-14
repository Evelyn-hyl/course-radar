import type { ReactNode } from 'react';
import type { HealthStatus } from '../services/api';
import { ConnectionStatus } from './ConnectionStatus';

type ChatLayoutProps = {
  status: HealthStatus;
  children: ReactNode;
  composer: ReactNode;
};

export function ChatLayout({ status, children, composer }: ChatLayoutProps) {
  return (
    <div className="min-h-dvh bg-background text-primary">
      <header className="fixed inset-x-0 top-0 z-10 border-b border-primary/8 bg-background/90 backdrop-blur-sm">
        <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-4 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-semibold text-background">C</div>
            <span className="font-semibold tracking-tight">CourseRadar</span>
          </div>
          <ConnectionStatus status={status} />
        </div>
      </header>
      <main className="mx-auto flex min-h-dvh w-full max-w-4xl flex-col px-4 pt-16 pb-44 sm:px-6">
        {children}
      </main>
      <div className="fixed inset-x-0 bottom-0 z-10 bg-gradient-to-t from-background via-background to-transparent px-4 pt-8 pb-[max(1rem,env(safe-area-inset-bottom))] sm:px-6">
        <div className="mx-auto max-w-3xl">{composer}</div>
      </div>
    </div>
  );
}

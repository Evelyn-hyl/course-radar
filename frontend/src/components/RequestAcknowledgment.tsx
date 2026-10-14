import { SoftLoader } from './SoftLoader';

type RequestAcknowledgmentProps = {
  message: string;
  isLoading: boolean;
};

export function RequestAcknowledgment({ message, isLoading }: RequestAcknowledgmentProps) {
  return (
    <div className="rounded-card border border-primary/10 bg-surface/55 p-5 text-primary">
      <p className="text-sm leading-6">{message}</p>
      {isLoading && <div className="mt-4"><SoftLoader /></div>}
    </div>
  );
}

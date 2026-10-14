import Markdown from 'react-markdown';
import rehypeKatex from 'rehype-katex';
import remarkMath from 'remark-math';

type MarkdownMathRendererProps = {
  content: string;
};

export function MarkdownMathRenderer({ content }: MarkdownMathRendererProps) {
  return (
    <div className="response-content">
      <Markdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>{content}</Markdown>
    </div>
  );
}

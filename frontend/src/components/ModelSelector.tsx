type Props = {
  value: string;
  onChange: (value: string) => void;
};

export default function ModelSelector({ value, onChange }: Props) {
  return (
    <label>
      اختيار النموذج
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="ensemble">Ensemble</option>
        <option value="arabert">AraBERT</option>
        <option value="xlmr">XLM-RoBERTa</option>
        <option value="llm">LLM + RAG</option>
      </select>
    </label>
  );
}

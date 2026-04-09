import { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const units = [
  "ADMAV Sede",
  "ADMAV Freguesia",
  "ADMAV Colônia",
  "MAV Recreio",
  "ADMAV Campo Grande",
  "ADMAV Praça Seca",
];

const initialForm = {
  name: "",
  phone: "",
  email: "",
  birth_date: "",
  marital_status: "",
  address: "",
  unit: units[0],
};

export default function App() {
  const [form, setForm] = useState(initialForm);
  const [status, setStatus] = useState({ type: "", message: "" });
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setStatus({ type: "", message: "" });

    try {
      const response = await fetch(`${API_URL}/members`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          email: form.email || null,
          birth_date: form.birth_date || null,
          marital_status: form.marital_status || null,
          address: form.address || null,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Falha ao cadastrar membro.");
      }

      const member = await response.json();
      setStatus({
        type: "success",
        message: `${member.name} cadastrado com sucesso na unidade ${member.unit}.`,
      });
      setForm({ ...initialForm });
    } catch (error) {
      setStatus({
        type: "error",
        message: error.message,
      });
    } finally {
      setLoading(false);
    }
  }

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">ADMAV AI CHURCH SYSTEM</p>
        <h1>Cadastro inteligente de membros</h1>
        <p className="lead">
          Estrutura inicial em React para registrar novos membros e enviar os dados
          diretamente ao backend FastAPI.
        </p>
      </section>

      <section className="panel">
        <form className="member-form" onSubmit={handleSubmit}>
          <label>
            Nome
            <input name="name" value={form.name} onChange={updateField} required />
          </label>

          <label>
            Telefone
            <input name="phone" value={form.phone} onChange={updateField} required />
          </label>

          <label>
            Email
            <input name="email" type="email" value={form.email} onChange={updateField} />
          </label>

          <label>
            Data de nascimento
            <input name="birth_date" type="date" value={form.birth_date} onChange={updateField} />
          </label>

          <label>
            Estado civil
            <input name="marital_status" value={form.marital_status} onChange={updateField} />
          </label>

          <label>
            Endereço
            <textarea name="address" rows="3" value={form.address} onChange={updateField} />
          </label>

          <label>
            Unidade
            <select name="unit" value={form.unit} onChange={updateField} required>
              {units.map((unit) => (
                <option key={unit} value={unit}>
                  {unit}
                </option>
              ))}
            </select>
          </label>

          <button type="submit" disabled={loading}>
            {loading ? "Enviando..." : "Cadastrar membro"}
          </button>
        </form>

        <aside className="notes">
          <h2>Unidades</h2>
          <ul>
            {units.map((unit) => (
              <li key={unit}>{unit}</li>
            ))}
          </ul>
          {status.message ? <p className={`status ${status.type}`}>{status.message}</p> : null}
        </aside>
      </section>
    </main>
  );
}

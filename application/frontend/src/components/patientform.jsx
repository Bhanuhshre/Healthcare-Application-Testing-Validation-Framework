import { useState } from "react";
import { api } from "../api/client";

const initialForm = {
  full_name: "",
  date_of_birth: "",
  contact_number: "",
  email: "",
};

export default function PatientForm({ onCreated }) {
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const payload = {
        ...form,
        date_of_birth: new Date(form.date_of_birth).toISOString(),
        email: form.email || null,
      };
      await api.createPatient(payload);
      setForm(initialForm);
      onCreated?.();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h3>Register patient</h3>
      {error && <p role="alert">{error}</p>}

      <label htmlFor="full_name">Full name</label>
      <input
        id="full_name"
        name="full_name"
        value={form.full_name}
        onChange={handleChange}
        required
      />

      <label htmlFor="date_of_birth">Date of birth</label>
      <input
        id="date_of_birth"
        name="date_of_birth"
        type="date"
        value={form.date_of_birth}
        onChange={handleChange}
        required
      />

      <label htmlFor="contact_number">Contact number</label>
      <input
        id="contact_number"
        name="contact_number"
        value={form.contact_number}
        onChange={handleChange}
        required
      />

      <label htmlFor="email">Email (optional)</label>
      <input id="email" name="email" type="email" value={form.email} onChange={handleChange} />

      <button type="submit" disabled={submitting}>
        {submitting ? "Saving..." : "Register patient"}
      </button>
    </form>
  );
}

import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function PatientList({ refreshKey }) {
  const [patients, setPatients] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .listPatients()
      .then(setPatients)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [refreshKey]);

  if (loading) return <p>Loading patients...</p>;
  if (error) return <p role="alert">Could not load patients: {error}</p>;
  if (patients.length === 0) return <p>No patients on record yet.</p>;

  return (
    <table>
      <thead>
        <tr>
          <th>MRN</th>
          <th>Name</th>
          <th>Contact number</th>
          <th>Email</th>
        </tr>
      </thead>
      <tbody>
        {patients.map((p) => (
          <tr key={p.id}>
            <td>{p.medical_record_number}</td>
            <td>{p.full_name}</td>
            <td>{p.contact_number}</td>
            <td>{p.email || "-"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

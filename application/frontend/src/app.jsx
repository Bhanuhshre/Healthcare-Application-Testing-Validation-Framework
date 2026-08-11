import { useState } from "react";
import LoginForm from "./components/LoginForm";
import PatientList from "./components/PatientList";
import PatientForm from "./components/PatientForm";

export default function App() {
  const [token, setToken] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  if (!token) {
    return (
      <main>
        <h1>Clinic Scheduling</h1>
        <LoginForm onLoggedIn={setToken} />
      </main>
    );
  }

  return (
    <main>
      <h1>Clinic Scheduling</h1>
      <PatientForm onCreated={() => setRefreshKey((k) => k + 1)} />
      <PatientList refreshKey={refreshKey} />
    </main>
  );
}

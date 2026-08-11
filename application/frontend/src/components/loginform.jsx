import { useState } from "react";
import { api, setAuthToken } from "../api/client";

export default function LoginForm({ onLoggedIn }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    try {
      const { access_token } = await api.login(email, password);
      setAuthToken(access_token);
      onLoggedIn(access_token);
    } catch (err) {
      setError("Invalid email or password");
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h3>Staff login</h3>
      {error && <p role="alert">{error}</p>}

      <label htmlFor="email">Email</label>
      <input
        id="email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />

      <label htmlFor="password">Password</label>
      <input
        id="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />

      <button type="submit">Log in</button>
    </form>
  );
}

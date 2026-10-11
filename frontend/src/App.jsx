import { useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;
const FEATURE_LABELS = {
  person_age: "Age",
  person_income: "Annual Income",
  person_home_ownership: "Home Ownership",
  person_emp_length: "Employment Length",
  loan_intent: "Loan Purpose",
  loan_amnt: "Loan Amount",
  loan_percent_income: "Loan-to-Income Ratio",
  cb_person_default_on_file: "Previous Default",
  cb_person_cred_hist_length: "Credit History Length",
};

function getFeatureLabel(feature) {
  return FEATURE_LABELS[feature] || feature;
}
function App() {
  const [formData, setFormData] = useState({
    person_age: 30,
    person_income: 60000,
    person_home_ownership: "RENT",
    person_emp_length: 5,
    loan_intent: "PERSONAL",
    loan_amnt: 10000,
    loan_percent_income: 0.17,
    cb_person_default_on_file: "N",
    cb_person_cred_hist_length: 5,
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleChange(event) {
    const { name, value, type } = event.target;

    setFormData((current) => ({
      ...current,
      [name]: type === "number" ? Number(value) : value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();

        throw new Error(
          errorData.detail
            ? JSON.stringify(errorData.detail)
            : "Prediction request failed"
        );
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="container">
        <h1>Credit Risk Assessment</h1>

        <p className="subtitle">
          Enter applicant and loan information to estimate default risk.
        </p>

        <form onSubmit={handleSubmit} className="form">
          <label>
            Age
            <input
              type="number"
              name="person_age"
              value={formData.person_age}
              onChange={handleChange}
              min="18"
              max="100"
              required
            />
          </label>

          <label>
            Annual Income ($)
            <input
              type="number"
              name="person_income"
              value={formData.person_income}
              onChange={handleChange}
              min="1"
              required
            />
          </label>

          <label>
            Home Ownership
            <select
              name="person_home_ownership"
              value={formData.person_home_ownership}
              onChange={handleChange}
            >
              <option value="RENT">Rent</option>
              <option value="MORTGAGE">Mortgage</option>
              <option value="OWN">Own</option>
              <option value="OTHER">Other</option>
            </select>
          </label>

          <label>
            Employment Length (years)
            <input
              type="number"
              name="person_emp_length"
              value={formData.person_emp_length}
              onChange={handleChange}
              min="0"
              required
            />
          </label>

          <label>
            Loan Purpose
            <select
              name="loan_intent"
              value={formData.loan_intent}
              onChange={handleChange}
            >
              <option value="PERSONAL">Personal</option>
              <option value="EDUCATION">Education</option>
              <option value="MEDICAL">Medical</option>
              <option value="VENTURE">Venture</option>
              <option value="HOMEIMPROVEMENT">Home Improvement</option>
              <option value="DEBTCONSOLIDATION">Debt Consolidation</option>
            </select>
          </label>

          <label>
            Loan Amount ($)
            <input
              type="number"
              name="loan_amnt"
              value={formData.loan_amnt}
              onChange={handleChange}
              min="1"
              required
            />
          </label>

          <label>
            Loan / Income Ratio
            <input
              type="number"
              step="0.01"
              name="loan_percent_income"
              value={formData.loan_percent_income}
              onChange={handleChange}
              min="0"
              max="1"
              required
            />
          </label>

          <label>
            Previous Default
            <select
              name="cb_person_default_on_file"
              value={formData.cb_person_default_on_file}
              onChange={handleChange}
            >
              <option value="N">No</option>
              <option value="Y">Yes</option>
            </select>
          </label>

          <label>
            Credit History Length (years)
            <input
              type="number"
              name="cb_person_cred_hist_length"
              value={formData.cb_person_cred_hist_length}
              onChange={handleChange}
              min="0"
              required
            />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? "Assessing..." : "Assess Risk"}
          </button>
        </form>

        {error && <div className="error">{error}</div>}

        {result && (
          <div className="result">
            <h2>Assessment Result</h2>

            <p>
              <strong>Default Probability:</strong>{" "}
              {(result.default_probability * 100).toFixed(1)}%
            </p>

            <p>
              <strong>Risk:</strong>{" "}
                <span
                  className={
                    result.risk_label === "High Risk"
                      ? "risk-badge red"
                      : "risk-badge green"
                  }
                >
                  {result.risk_label === "High Risk" ? "High Risk" : "Low Risk"}
                 </span>
            </p>

            <p>
              <strong>Prediction ID:</strong> {result.prediction_id}
            </p>

            <h3>Factors Increasing Risk</h3>

            <ul>
              {result.increasing_risk.map((item, index) => (
                <li key={index}>
                  {getFeatureLabel(item.feature)}: {item.value}
                </li>
              ))}
            </ul>

            <h3>Factors Reducing Risk</h3>

            <ul>
              {result.decreasing_risk.map((item, index) => (
                <li key={index}>
                  {getFeatureLabel(item.feature)}: {item.value}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
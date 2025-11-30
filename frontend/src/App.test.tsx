import React from "react";
import { render, screen } from "@testing-library/react";
import App from "./App";

test("renders MoneySplit app", () => {
  render(<App />);
  const appElements = screen.getAllByText(/MoneySplit/i);
  expect(appElements.length).toBeGreaterThan(0);
  expect(appElements[0]).toBeInTheDocument();
});

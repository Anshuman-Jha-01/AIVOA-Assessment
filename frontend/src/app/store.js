import { configureStore } from "@reduxjs/toolkit";
import complaintDraftReducer from "../features/complaints/complaintDraftSlice";
import copilotReducer from "../features/copilot/copilotSlice";
import dashboardReducer from "../features/dashboard/dashboardSlice";

export const store = configureStore({
  reducer: {
    complaintDraft: complaintDraftReducer,
    copilot: copilotReducer,
    dashboard: dashboardReducer,
  },
});

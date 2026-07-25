import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { complaintsApi } from "../../api/client";

const emptyFields = {
  complaint_source: "",
  customer_name: "",
  product_name: "",
  product_strength: "",
  batch_lot_number: "",
  affected_quantity: "",
  manufacturing_date: "",
  expiry_date: "",
  originating_site_block: "",
  impacted_npm: "",
  complaint_category: "",
  complaint_description: "",
};

const emptyAssessment = {
  ai_severity_suggested: "",
  ai_suggested_next_action: "",
  ai_initial_risk_assessment: "",
  ai_root_cause_suggestion: "",
  ai_capa_suggestion: "",
  ai_summary: "",
  ai_completeness_notes: "",
};

export const commitComplaint = createAsyncThunk(
  "complaintDraft/commit",
  async (_, { getState }) => {
    const { fields, assessment } = getState().complaintDraft;
    return complaintsApi.commit({ ...fields, ...assessment });
  }
);

const initialState = {
  fields: emptyFields,
  assessment: emptyAssessment,
  duplicates: [],
  status: "PENDING_TRIAGE", // PENDING_TRIAGE -> READY_TO_COMMIT -> COMMITTED
  committing: false,
  committed: null,
};

const complaintDraftSlice = createSlice({
  name: "complaintDraft",
  initialState,
  reducers: {
    mergeFields(state, action) {
      Object.entries(action.payload).forEach(([k, v]) => {
        if (v !== null && v !== undefined && v !== "") {
          state.fields[k] = v;
        }
      });
      // Once we have the core identifying info, the form is ready to commit.
      if (state.fields.product_name && state.fields.batch_lot_number) {
        state.status = "READY_TO_COMMIT";
      }
    },
    mergeAssessment(state, action) {
      Object.entries(action.payload).forEach(([k, v]) => {
        if (v !== null && v !== undefined && v !== "") {
          state.assessment[k] = v;
        }
      });
    },
    setDuplicates(state, action) {
      state.duplicates = action.payload;
    },
    setField(state, action) {
      const { field, value } = action.payload;
      state.fields[field] = value;
    },
    resetDraft(state) {
      state.fields = emptyFields;
      state.assessment = emptyAssessment;
      state.duplicates = [];
      state.status = "PENDING_TRIAGE";
      state.committed = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(commitComplaint.pending, (state) => {
        state.committing = true;
      })
      .addCase(commitComplaint.fulfilled, (state, action) => {
        state.committing = false;
        state.status = "COMMITTED";
        state.committed = action.payload;
      })
      .addCase(commitComplaint.rejected, (state) => {
        state.committing = false;
      });
  },
});

export const { mergeFields, mergeAssessment, setDuplicates, setField, resetDraft } =
  complaintDraftSlice.actions;
export default complaintDraftSlice.reducer;

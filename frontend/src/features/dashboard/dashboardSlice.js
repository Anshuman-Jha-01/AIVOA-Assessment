import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { complaintsApi } from "../../api/client";

export const fetchComplaints = createAsyncThunk("dashboard/fetchComplaints", async () => {
  return complaintsApi.list();
});

export const fetchDashboardStats = createAsyncThunk("dashboard/fetchStats", async () => {
  return complaintsApi.dashboardStats();
});

const initialState = {
  complaints: [],
  stats: { total: 0, pending_triage: 0, ready_to_commit: 0, committed: 0, critical: 0, major: 0, minor: 0 },
  loading: false,
};

const dashboardSlice = createSlice({
  name: "dashboard",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchComplaints.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchComplaints.fulfilled, (state, action) => {
        state.loading = false;
        state.complaints = action.payload;
      })
      .addCase(fetchComplaints.rejected, (state) => {
        state.loading = false;
      })
      .addCase(fetchDashboardStats.fulfilled, (state, action) => {
        state.stats = action.payload;
      });
  },
});

export default dashboardSlice.reducer;

import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { copilotApi } from "../../api/client";
import { mergeFields, mergeAssessment, setDuplicates } from "../complaints/complaintDraftSlice";

function makeSessionId() {
  return "session_" + Math.random().toString(36).slice(2) + Date.now().toString(36);
}

export const sendCopilotMessage = createAsyncThunk(
  "copilot/sendMessage",
  async (message, { getState, dispatch }) => {
    const { sessionId } = getState().copilot;
    const { fields } = getState().complaintDraft;
    const response = await copilotApi.sendMessage(sessionId, message, fields);
    dispatch(mergeFields(response.fields));
    dispatch(mergeAssessment(response.assessment));
    dispatch(setDuplicates(response.duplicates || []));
    return response;
  }
);

export const uploadCopilotFile = createAsyncThunk(
  "copilot/uploadFile",
  async (file, { getState, dispatch }) => {
    const { sessionId } = getState().copilot;
    const { fields } = getState().complaintDraft;
    const response = await copilotApi.upload(sessionId, file, fields);
    dispatch(mergeFields(response.fields));
    dispatch(mergeAssessment(response.assessment));
    dispatch(setDuplicates(response.duplicates || []));
    return response;
  }
);

const initialState = {
  sessionId: makeSessionId(),
  messages: [
    {
      role: "assistant",
      content:
        "Ready to process new complaints. You can paste the raw email from the customer, or upload a PDF of the complaint report. I will extract the data and run the initial risk assessment.",
    },
  ],
  pendingFile: null, // { name } shown as an attachment bubble while uploading
  loading: false,
  error: null,
};

const copilotSlice = createSlice({
  name: "copilot",
  initialState,
  reducers: {
    addUserMessage(state, action) {
      state.messages.push({ role: "user", content: action.payload });
    },
    addFileMessage(state, action) {
      state.messages.push({ role: "user", content: action.payload, isFile: true });
    },
    resetSession(state) {
      state.sessionId = makeSessionId();
      state.messages = initialState.messages;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendCopilotMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(sendCopilotMessage.fulfilled, (state, action) => {
        state.loading = false;
        state.messages.push({ role: "assistant", content: action.payload.reply });
      })
      .addCase(sendCopilotMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
        state.messages.push({
          role: "assistant",
          content: "Sorry, I ran into an error processing that. Please try again.",
        });
      })
      .addCase(uploadCopilotFile.pending, (state) => {
        state.loading = true;
      })
      .addCase(uploadCopilotFile.fulfilled, (state, action) => {
        state.loading = false;
        state.messages.push({ role: "assistant", content: action.payload.reply });
      })
      .addCase(uploadCopilotFile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
        state.messages.push({
          role: "assistant",
          content: "Sorry, I couldn't process that file. Please try again.",
        });
      });
  },
});

export const { addUserMessage, addFileMessage, resetSession } = copilotSlice.actions;
export default copilotSlice.reducer;

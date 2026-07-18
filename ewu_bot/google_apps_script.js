const SPREADSHEET_ID = "109Mfs9ZTOqkfN4-UhMGsGBnE4oSJtHSHEF7dTjLzBjw";

const SHEETS = {
  "EWU Leads": [
    "Date", "EWU_ID", "Type", "Name", "Language", "Phone", "Source", "Status", "Comment"
  ],
  "EWU Operations": [
    "EWU_ID", "Type", "Full_Name", "First_Name", "Last_Name", "Date_of_birth", "Nationality",
    "Current_country", "Current_city", "Profession", "Experience", "Welding_methods",
    "Foreign_experience", "Countries_worked_in", "Language_skills", "Certificates",
    "Certificate_validity", "Documents", "Relocation_readiness", "Preferred_countries",
    "Overtime", "Travel_ready", "Team_lead_experience", "Phone", "Telegram", "WhatsApp",
    "Email", "Photo", "Driving_Licence", "Driving_Categories", "Own_Vehicle",
    "Company", "Contact_person", "Country", "City", "Vacancy", "Quantity",
    "Project_description", "Contract_type", "Salary", "Working_hours", "Shifts",
    "Accommodation", "Transport", "Work_clothing", "Meals", "Starting_date",
    "Production_Photos", "Accommodation_Photos", "Topic", "Description", "Destination",
    "Family_need", "Business_topic", "Training_topic", "Concern", "Membership_Status",
    "Referral_Status", "Reward_Eligibility", "Referring_member", "Referred_worker",
    "Drawings", "Countries", "Certificate_Document", "Certificate_Document_Verified",
    "Certificate_Document_Photos", "Certificate_Verification_Status", "Work_Photos",
    "Work_Photo_Files", "Travel", "Qualification_Score", "Qualification_Level",
    "Qualification_Rating", "Salary_PL", "Salary_DE",
    "Employer_Assignment", "AI_Summary", "Current_Status"
  ],
  "Pipeline": [
    "EWU_ID", "Current_stage", "Transition_date", "Responsible_manager", "Next_step", "Deadline"
  ],
  "EWU Backup": [
    "Backup_date", "Table", "Payload"
  ],
  "EWU Admin Log": [
    "Date", "Action", "EWU_ID", "Payload"
  ]
};

function setupEWUCRM() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  Object.keys(SHEETS).forEach(name => {
    let sh = ss.getSheetByName(name);
    if (!sh) sh = ss.insertSheet(name);
    sh.clear();
    const headers = SHEETS[name];
    sh.getRange(1, 1, 1, headers.length).setValues([headers]);
    sh.getRange(1, 1, 1, headers.length)
      .setFontWeight("bold")
      .setBackground("#102E46")
      .setFontColor("#FFFFFF");
    sh.setFrozenRows(1);
    sh.autoResizeColumns(1, headers.length);
  });
}

function doGet() {
  return out({ ok: true, message: "EWU CRM working" });
}

function doPost(e) {
  try {
    const body = JSON.parse((e.postData && e.postData.contents) || "{}");
    const action = body.action || "upsert";
    const table = body.table || "EWU Leads";
    const data = body.data || {};

    if (action === "update_status") {
      return out(updateStatus(
        data.EWU_ID || body.ewu_id,
        data.Current_stage || body.status,
        data.Responsible_manager || body.coordinator || ""
      ));
    }

    if (action === "pipeline") {
      appendRow("Pipeline", data);
      backup("Pipeline", data);
      return out({ ok: true, table: "Pipeline", ewu_id: data.EWU_ID || "" });
    }

    upsertRow(table, data);
    backup(table, data);
    return out({ ok: true, table: table, ewu_id: data.EWU_ID || "" });
  } catch (err) {
    return out({ ok: false, error: String(err) });
  }
}

function upsertRow(table, data) {
  const sh = getSheet(table);
  const headers = getHeaders(sh);
  const idIndex = headers.indexOf("EWU_ID") + 1;
  if (!data.EWU_ID || idIndex < 1) {
    appendRow(table, data);
    return;
  }
  const lastRow = sh.getLastRow();
  if (lastRow > 1) {
    const ids = sh.getRange(2, idIndex, lastRow - 1, 1).getValues();
    for (let i = 0; i < ids.length; i++) {
      if (String(ids[i][0]) === String(data.EWU_ID)) {
        sh.getRange(i + 2, 1, 1, headers.length).setValues([headers.map(h => valueForHeader(h, data))]);
        return;
      }
    }
  }
  appendRow(table, data);
}

function appendRow(table, data) {
  const sh = getSheet(table);
  const headers = getHeaders(sh);
  sh.appendRow(headers.map(h => valueForHeader(h, data)));
}

function valueForHeader(header, data) {
  if (header === "Date" || header === "Transition_date" || header === "Backup_date") {
    return data[header] || new Date();
  }
  if (header === "Payload") return JSON.stringify(data);
  return data[header] || "";
}

function getSheet(table) {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  let sh = ss.getSheetByName(table);
  if (!sh) {
    sh = ss.insertSheet(table);
    const headers = SHEETS[table] || SHEETS["EWU Leads"];
    sh.getRange(1, 1, 1, headers.length).setValues([headers]);
  }
  return sh;
}

function getHeaders(sh) {
  return sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0];
}

function backup(table, data) {
  const sh = getSheet("EWU Backup");
  sh.appendRow([new Date(), table, JSON.stringify(data)]);
}

function updateStatus(id, status, coordinator) {
  appendRow("Pipeline", {
    EWU_ID: id,
    Current_stage: status,
    Transition_date: new Date(),
    Responsible_manager: coordinator,
    Next_step: "",
    Deadline: ""
  });
  return { ok: true, ewu_id: id, status: status };
}

function out(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

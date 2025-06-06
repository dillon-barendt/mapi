# 🏟️ **Row-Progression Suite: Comprehensive API Toolkit** ✨

## **🚀 Overview**

The **Row-Progression Suite** is a FastAPI-based toolkit designed to simplify **parsing**, **generating**, and **diffing row progression codes**, facilitating the creation and management of structured venue configurations. This app offers powerful tools for working with **section-row mappings** in **ticket marketplaces**, enabling efficient workflows with row progression data and dynamic schema validations.


## **📋 Key Features**

- 🔍 **Parse** row progression codes into structured models (with strict validation).
- 🛠️ **Build** comprehensive venue configurations with logical row mappings and sections.
- 🆚 **Diff** venues to track changes and mismatched sections/rows.
- 📦 **Generate compressed representations** of section data for efficient storage and transmission.
- 💥 Rich support for **row progression logic**, including **slicing**, **equivalent rows**, and **gaps**.



## **🧩 Core Concepts**

### **1. Row Progression Codes**

A **row progression code** is a convenient string representation describing row names and positions within a section. These codes can be as simple or as complex as needed.

#### **Examples**:
1. Simple code: `"1:3"`  
   - Describes 3 rows: `1`, `2`, and `3`, with positions 1, 2, and 3.

2. Complex code: `"DD:AA,A:C,1:4,5!,6:10:2,12=12W,ZZZ"`  
   - Describes rows:
     - `DD = 1`, `CC = 2`, `BB = 3`, `AA = 4`, `A = 5`, `B = 6`, `C = 7`, `1 = 8`, `12W = 16`, and `ZZZ = 17`.

#### **Advanced Features of Row Progressions**:
- 🎭 **Equivalent Rows**: Use `=` to indicate rows with equal positions (e.g., `3=3W`).
- 🚀 **Row Slices**: Define ranges using `:` with optional stepping (`A:D:2`, `1:4:2`).
- 🚫 **Gap Slices**: Mark gaps with `!` to exclude them from sections (`A:C!`).

---

### **2. Atomic Codes**

Atomic codes represent individual rows. They come in two kinds:
1. **Pure** (e.g., `A`, `AA`, `1`, `123`).
2. **Mixed** (e.g., `B10`, `21WC`).

#### **Pure Atomic Code Types**:
- `NUMBERS` (e.g., `1`, `2`, `3`).
- `LETTERS_1` (e.g., `A`, `B`, `C`).
- `LETTERS_2` (e.g., `AA`, `BB`, `CC`).

Atomic codes are validated to ensure consistency 🌟.


### **3. Venue Models**

#### **Building Venues 🌟**
- Each **venue** is composed of **sections**, and each section has a **row progression code** that determines its rows.
- Example Workflow:
  1. Define venue name and sections.
  2. Parse row progression codes for sections.
  3. Validate row uniqueness across sections.


### **4. Programmatic APIs**

- **`/build-venue` Endpoint**:
  Constructs and validates a venue based on the request body. Dynamically parses row progressions for sections and calculates the total row count.

- **`/venue-diff` Endpoint**:
  Compares two venues and identifies mismatched rows/sections to flag configuration changes.

- **`/generate` Endpoint**:
  Compresses row and section data into a compact representation, reducing storage overhead.

- **`/slice-info` Endpoint**:
  Provides details on row slices, including type (single, slice, gap, equivalent), position ranges, and more.


## **🛠️ API Examples**
Here are some common use cases with their corresponding input and output.

### **1. Build Venue**
**Request**:
```json
POST /build-venue
{
  "venue_name": "Big Bowl Stadium",
  "sections": [
    { "name": "101", "code": "A:C,1:3" },
    { "name": "102", "code": "D:F,G:H!" }
  ]
}
```


**Response**:
```json
{
  "venue_name": "Big Bowl Stadium",
  "sections": [
    {
      "name": "101",
      "rows": [
        { "name": "A", "position": 1 },
        { "name": "B", "position": 2 },
        { "name": "C", "position": 3 },
        { "name": "1", "position": 4 },
        { "name": "2", "position": 5 },
        { "name": "3", "position": 6 }
      ]
    },
    {
      "name": "102",
      "rows": [
        { "name": "D", "position": 1 },
        { "name": "E", "position": 2 },
        { "name": "F", "position": 3 }
      ]
    }
  ],
  "total_rows": 9
}
```


---

### **2. Venue Diff**
**Request**:
```json
POST /venue-diff
{
  "a": {
    "name": "Old Venue",
    "sections": {"101": "A:C,1:3"}
  },
  "b": {
    "name": "New Venue",
    "sections": {"101": "1:C", "102": "X:Z"}
  }
}
```


**Response**:
```json
{
  "venue_diff": {
    "101": {
      "A": { "a": 1, "b": null }, 
      "B": { "a": 2, "b": null }
    },
    "102": {
      "X": { "a": null, "b": 1 },
      "Y": { "a": null, "b": 2 },
      "Z": { "a": null, "b": 3 }
    }
  }
}
```


## **🔮 Behind the Scenes: Parsing Logic**

The **row progression parser** powers much of the suite's capabilities. It breaks down row codes into structured models and supports advanced parsing rules.

#### **Highlights**:
- Converts row slices (e.g., `"A:C"`) into row sequences (`A, B, C`).
- Identifies gaps via `!` and equivalent rows via `=`.

Example with `"A:C!,D:F,E:G=H"`:
- Output:  
  - Gap Rows: `"A:C"` (excluded from positions).
  - Equivalent Rows: `"E:G=H"` (grouped under shared position).


## **🎉 Why Use This Toolkit?**

- 🌟 **Simple & Powerful**: Intuitive APIs for complex venue data.
- 🔍 **Robust Validation**: Rigorous checks on input to ensure data consistency.
- ⚡ **High Performance**: Efficient parsing and computation of row progressions.
- 🔧 **Customizable**: Extendable for different venues and progression rules.


## 💻 **Getting Started**

### **Install Dependencies**
```shell script
pip install fastapi uvicorn pydantic
```

### **Run the App**
```shell script
uvicorn app.main:app --reload
```

### **Access API Docs**
Visit the interactive Swagger UI at `http://127.0.0.1:8000/docs`.

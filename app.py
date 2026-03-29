import yfinance as yf
import streamlit as st
from openai import OpenAI

client = OpenAI(api_key="")
   info = stock.info
   data = {
       "company": info.get("longName"),
       "sector": info.get("sector"),
       "market_cap": info.get("marketCap"),
       "pe_ratio": info.get("trailingPE"),
       "revenue": info.get("totalRevenue")
   }
   prompt = f"""
   You are a professional equity analyst.
   Analyze this company using the data below:
   {data}
   Provide:
   - Overview
   - Business Model
   - Financial Snapshot
   - Risks
   - Investment Thesis
   """
   response = client.responses.create(
       model="gpt-4.1",
       input=prompt
   )
   st.write(response.output_text)

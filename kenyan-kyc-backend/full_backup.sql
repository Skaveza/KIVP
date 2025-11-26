--
-- PostgreSQL database dump
--

\restrict dmSiJ61Jppt0vPWqQUgccPaJwf9xfdFCOuAf6OT4KFjnkMHs4HLnmnMo3YZNGhy

-- Dumped from database version 15.15 (Homebrew)
-- Dumped by pg_dump version 15.15 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: macbook
--

CREATE TABLE public.audit_logs (
    id uuid NOT NULL,
    user_id uuid,
    action_type character varying(50) NOT NULL,
    entity_type character varying(50),
    entity_id uuid,
    action_description text,
    old_value jsonb,
    new_value jsonb,
    ip_address inet,
    user_agent text,
    created_at timestamp without time zone
);


ALTER TABLE public.audit_logs OWNER TO macbook;

--
-- Name: receipts; Type: TABLE; Schema: public; Owner: macbook
--

CREATE TABLE public.receipts (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    file_name character varying(255) NOT NULL,
    file_path character varying(500) NOT NULL,
    file_size integer,
    file_type character varying(50),
    status character varying(20),
    processing_started_at timestamp without time zone,
    processing_completed_at timestamp without time zone,
    error_message text,
    company_name character varying(255),
    receipt_date date,
    receipt_address text,
    total_amount numeric(10,2),
    currency character varying(3),
    confidence_company numeric(3,2),
    confidence_date numeric(3,2),
    confidence_address numeric(3,2),
    confidence_total numeric(3,2),
    overall_confidence numeric(3,2),
    raw_extraction_json jsonb,
    uploaded_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.receipts OWNER TO macbook;

--
-- Name: users; Type: TABLE; Schema: public; Owner: macbook
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    full_name character varying(255) NOT NULL,
    phone_number character varying(20),
    national_id character varying(50),
    kyc_status character varying(20),
    kyc_score numeric(5,2),
    verification_date timestamp without time zone,
    account_type character varying(20),
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    last_login timestamp without time zone
);


ALTER TABLE public.users OWNER TO macbook;

--
-- Name: verification_scores; Type: TABLE; Schema: public; Owner: macbook
--

CREATE TABLE public.verification_scores (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    document_quality_score numeric(5,2),
    spending_pattern_score numeric(5,2),
    consistency_score numeric(5,2),
    diversity_score numeric(5,2),
    final_score numeric(5,2),
    is_verified boolean,
    verification_threshold numeric(5,2),
    total_receipts integer,
    total_spending numeric(12,2),
    unique_companies integer,
    unique_locations integer,
    date_range_days integer,
    average_transaction_amount numeric(10,2),
    calculated_at timestamp without time zone
);


ALTER TABLE public.verification_scores OWNER TO macbook;

--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: macbook
--

COPY public.audit_logs (id, user_id, action_type, entity_type, entity_id, action_description, old_value, new_value, ip_address, user_agent, created_at) FROM stdin;
\.


--
-- Data for Name: receipts; Type: TABLE DATA; Schema: public; Owner: macbook
--

COPY public.receipts (id, user_id, file_name, file_path, file_size, file_type, status, processing_started_at, processing_completed_at, error_message, company_name, receipt_date, receipt_address, total_amount, currency, confidence_company, confidence_date, confidence_address, confidence_total, overall_confidence, raw_extraction_json, uploaded_at, updated_at) FROM stdin;
07ec3770-f4aa-4164-82b5-8bd44a55a90d	425c68c8-e693-43f1-a8f9-fce50aad5f38	test2.jpg	tests/demo_receipts/test2.jpg	\N	\N	completed	\N	\N	\N	NATVAS LTDESTLANDS BRANCH	2815-11-17		2132779.00	KES	0.95	0.95	0.95	0.95	0.95	\N	2025-11-19 15:23:33.346552	2025-11-19 17:23:29.731662
74340cc8-9cff-4a4a-aa54-44967f139f93	425c68c8-e693-43f1-a8f9-fce50aad5f38	test5.jpeg	tests/demo_receipts/test5.jpeg	\N	\N	completed	\N	\N	\N	NAIROBI JAVA HOUSE LTD. JAVA PARKLANDS	\N	P.O BOX 21533 - 00505	410.00	KES	0.97	0.97	0.97	0.97	0.97	\N	2025-11-19 15:23:34.488374	2025-11-19 17:23:29.731662
0713b022-3429-457c-b089-912cbb43db33	425c68c8-e693-43f1-a8f9-fce50aad5f38	test6.jpg	tests/demo_receipts/test6.jpg	\N	\N	completed	\N	\N	\N		\N		6450.00	KES	0.97	0.97	0.97	0.97	0.97	\N	2025-11-19 15:23:35.035921	2025-11-19 17:23:29.731662
2395362b-92fd-4c8c-98a5-08cf8f4d3bef	08241ece-9426-47f4-b879-4898cd637f87	test5.jpeg	./uploads/receipts/2395362b-92fd-4c8c-98a5-08cf8f4d3bef.jpeg	101140	image/jpeg	completed	2025-11-23 21:47:29.723998	2025-11-23 21:47:38.532395	\N	NAIROBI JAVA HOUSE LTD. JAVA PARKLANDS	\N	P.O BOX 21533 - 00505	410.00	KES	0.97	0.97	0.97	0.97	0.97	{"currency": "KES", "raw_text": " NAIROBI JAVA HOUSE LTD. JAVA PARKLANDS P.O BOX 21533 - 00505 0740 048 896 PIN: PO51126577H V.A.T: 01 118944, Parklands@javahouseafrica.com 2406 Fredrick Tbl 72/1 Chk 1828 Gst 11Jan'20 10:04 1 Oatmeal Half 1 Spark Water 0.5L 190.00 Food 220.00 Beverage 190.00 10:48 Total 410.00 16% VAT 55.09 BUY GOODS:717 643 HOW WAS YOUR JAVA EXPERIENCE TODAY? TEXT ‘ JAVA’ TO 0719 50 SO 50. THANK YOU, WELCOME AGAIN. Scan to Pay Hith MPESA", "confidence": 0.968826369678273, "raw_labels": ["B-company", "B-company", "I-company", "I-company", "I-company", "I-company", "I-company", "I-company", "I-company", "B-company", "I-company", "I-company", "I-company", "I-company", "I-company", "B-address", "B-address", "I-address", "I-address", "I-address", "I-address", "I-address", "I-address", "I-address", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "B-total", "B-total", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O"], "raw_tokens": ["ĠNA", "IRO", "BI", "ĠJ", "AV", "A", "ĠHOUSE", "ĠLTD", ".", "ĠJ", "AV", "A", "ĠPARK", "LAN", "DS", "ĠP", ".", "O", "ĠBOX", "Ġ215", "33", "Ġ-", "Ġ00", "505", "Ġ07", "40", "Ġ0", "48", "Ġ8", "96", "ĠPIN", ":", "ĠPO", "51", "12", "65", "77", "H", "ĠV", ".", "A", ".", "T", ":", "Ġ01", "Ġ11", "89", "44", ",", "ĠPark", "lands", "@", "j", "av", "ah", "ouse", "af", "rica", ".", "com", "Ġ240", "6", "ĠFred", "rick", "ĠT", "bl", "Ġ72", "/", "1", "ĠCh", "k", "Ġ18", "28", "ĠG", "st", "Ġ11", "Jan", "'", "20", "Ġ10", ":", "04", "Ġ1", "ĠO", "atmeal", "ĠHalf", "Ġ1", "ĠSpark", "ĠWater", "Ġ0", ".", "5", "L", "Ġ190", ".", "00", "ĠFood", "Ġ220", ".", "00", "ĠBever", "age", "Ġ190", ".", "00", "Ġ10", ":", "48", "ĠTotal", "Ġ410", ".", "00", "Ġ16", "%", "ĠVAT", "Ġ55", ".", "09", "ĠBU", "Y", "ĠGOOD", "S", ":", "7", "17", "Ġ6", "43", "ĠHOW", "ĠWAS", "ĠYOUR", "ĠJ", "AV", "A", "ĠEX", "PER", "IENCE", "ĠTODAY", "?", "ĠTEXT", "ĠâĢ", "ĺ", "ĠJ", "AV", "A", "âĢ", "Ļ", "ĠTO", "Ġ07", "19", "Ġ50", "ĠSO", "Ġ50", ".", "ĠTHANK", "ĠYOU", ",", "ĠW", "EL", "COM", "E", "ĠAGA", "IN", ".", "ĠScan", "Ġto", "ĠPay", "ĠH", "ith", "ĠMP", "ESA"], "company_name": "NAIROBI JAVA HOUSE LTD. JAVA PARKLANDS", "receipt_date": null, "total_amount": 410.0, "receipt_address": "P.O BOX 21533 - 00505"}	2025-11-23 21:47:29.723987	2025-11-23 23:47:29.741974
fe8d3570-af26-44dd-9f3d-aedffb839566	08241ece-9426-47f4-b879-4898cd637f87	test2.jpg	./uploads/receipts/fe8d3570-af26-44dd-9f3d-aedffb839566.jpg	165293	image/jpeg	completed	2025-11-23 21:47:42.33521	2025-11-23 21:47:47.148751	\N	NAIVAS LTDESTLANDS BRANCH	2815-11-17		9852886.00	KES	0.96	0.96	0.96	0.96	0.96	{"currency": "KES", "raw_text": " CHANGE NAIVAS LTD ‘ WESTLANDS BRANCH : P.0.BOX 61688-88188 NAIROBI TEL :828-2132779 FAX:026-2132 78 oe FP/09852886/08444D < IAT ww: 31a¢ PIN: Pas ’ peer 90086 USER: Cash Sale # 288-02180872665 Till No: 28-82 DateTime:11/17/2815 4:27:19 PM Store:28 ITEM QTY PRICE AMOUNT 14087376 4 x 15.00 FRESH FRUITY C/GUN 12 S 15.88 A (Nap robo 35) 50808182 EVEREADY BATT AAA 1012 2PACK 55.88 A 786.00 TOTAL CASH 4,800.80 938.88 VAT ANT", "confidence": 0.9607528970429772, "raw_labels": ["O", "O", "B-company", "B-company", "I-company", "I-company", "O", "O", "O", "I-company", "I-company", "I-company", "I-company", "I-company", "I-company", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O"], "raw_tokens": ["ĠCH", "ANGE", "ĠNA", "IV", "AS", "ĠLTD", "ĠâĢ", "ĺ", "ĠW", "EST", "LAN", "DS", "ĠBR", "AN", "CH", "Ġ:", "ĠP", ".", "0", ".", "BOX", "Ġ6", "16", "88", "-", "88", "188", "ĠNA", "IRO", "BI", "ĠT", "EL", "Ġ:", "8", "28", "-", "213", "27", "79", "ĠFA", "X", ":", "026", "-", "2", "132", "Ġ78", "Ġo", "e", "ĠFP", "/", "09", "85", "28", "86", "/", "08", "444", "D", "Ġ<", "ĠI", "AT", "Ġw", "w", ":", "Ġ31", "a", "Â¢", "ĠPIN", ":", "ĠPas", "ĠâĢ", "Ļ", "Ġpeer", "Ġ900", "86", "ĠUS", "ER", ":", "ĠCash", "ĠSale", "Ġ#", "Ġ288", "-", "02", "18", "08", "7", "26", "65", "ĠTill", "ĠNo", ":", "Ġ28", "-", "82", "ĠDate", "Time", ":", "11", "/", "17", "/", "28", "15", "Ġ4", ":", "27", ":", "19", "ĠPM", "ĠStore", ":", "28", "ĠIT", "EM", "ĠQ", "TY", "ĠPR", "ICE", "ĠAM", "OUNT", "Ġ14", "08", "7", "376", "Ġ4", "Ġx", "Ġ15", ".", "00", "ĠFR", "ESH", "ĠFR", "U", "ITY", "ĠC", "/", "G", "UN", "Ġ12", "ĠS", "Ġ15", ".", "88", "ĠA", "Ġ(", "Nap", "Ġro", "bo", "Ġ35", ")", "Ġ50", "808", "182", "ĠEVER", "E", "AD", "Y", "ĠB", "ATT", "ĠAAA", "Ġ101", "2", "Ġ2", "P", "ACK", "Ġ55", ".", "88", "ĠA", "Ġ7", "86", ".", "00", "ĠTOTAL", "ĠC", "ASH", "Ġ4", ",", "800", ".", "80", "Ġ9", "38", ".", "88", "ĠVAT", "ĠAN", "T"], "company_name": "NAIVAS LTDESTLANDS BRANCH", "receipt_date": "2815-11-17", "total_amount": 9852886.0, "receipt_address": ""}	2025-11-23 21:47:42.335204	2025-11-23 23:47:42.349699
6e3990e8-990d-45f4-8bf0-7954949a2b3c	4526d57b-07d2-4fa1-9d61-f9d4d03970c8	test5.jpeg	./uploads/receipts/6e3990e8-990d-45f4-8bf0-7954949a2b3c.jpeg	101140	image/jpeg	failed	2025-11-19 23:09:46.071424	2025-11-19 23:09:46.142415	\nLayoutLMv3ImageProcessor requires the PyTesseract library but it was not found in your environment. You can install it with pip:\n`pip install pytesseract`. Please note that you may need to restart your runtime after installation.\n	\N	\N	\N	\N	KES	\N	\N	\N	\N	\N	\N	2025-11-19 23:09:46.071418	2025-11-20 01:09:46.081222
da5e166d-6647-4e8d-a637-55ad93917fef	4526d57b-07d2-4fa1-9d61-f9d4d03970c8	test6.jpg	./uploads/receipts/da5e166d-6647-4e8d-a637-55ad93917fef.jpg	35801	image/jpeg	failed	2025-11-19 23:14:10.358428	2025-11-19 23:14:10.40642	\nLayoutLMv3ImageProcessor requires the PyTesseract library but it was not found in your environment. You can install it with pip:\n`pip install pytesseract`. Please note that you may need to restart your runtime after installation.\n	\N	\N	\N	\N	KES	\N	\N	\N	\N	\N	\N	2025-11-19 23:14:10.358424	2025-11-20 01:14:10.377418
6456d009-a714-4a80-a9c7-86bd17f7ac2d	4526d57b-07d2-4fa1-9d61-f9d4d03970c8	test5.jpeg	./uploads/receipts/6456d009-a714-4a80-a9c7-86bd17f7ac2d.jpeg	101140	image/jpeg	completed	2025-11-20 00:02:48.944465	2025-11-20 00:02:53.166702	\N	NAIROBI JAVA HOUSE LTD. JAVA PARKLANDS	\N	P.O BOX 21533 - 00505	410.00	KES	0.97	0.97	0.97	0.97	0.97	{"currency": "KES", "raw_text": " NAIROBI JAVA HOUSE LTD. JAVA PARKLANDS P.O BOX 21533 - 00505 0740 048 896 PIN: PO51126577H Y.A.T: 01 118944, parklands@javahouseafrica.com 2406 Fredrick Tb] 72/1 Chk 1828 Gst 11Jan'20 10:04 1 Oatmeal Half 1 Spark Water 0.5L 190.00 Food 220.00 Beverage 190.00 10:48 Total 410.00 16% VAT 55.99 BUY GOODS:717 643 HOW WAS YOUR JAVA EXPERIENCE TODAY? TEXT ‘ JAVA’ TO 0719 50 50 50. THANK YOU, WELCOME AGAIN. Scan to Pay Hith MPESA", "confidence": 0.9690328655187149, "raw_labels": ["B-company", "B-company", "I-company", "I-company", "I-company", "I-company", "I-company", "I-company", "I-company", "B-company", "I-company", "I-company", "I-company", "I-company", "I-company", "B-address", "B-address", "I-address", "I-address", "I-address", "I-address", "I-address", "I-address", "I-address", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "B-total", "B-total", "B-total", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O"], "raw_tokens": ["ĠNA", "IRO", "BI", "ĠJ", "AV", "A", "ĠHOUSE", "ĠLTD", ".", "ĠJ", "AV", "A", "ĠPARK", "LAN", "DS", "ĠP", ".", "O", "ĠBOX", "Ġ215", "33", "Ġ-", "Ġ00", "505", "Ġ07", "40", "Ġ0", "48", "Ġ8", "96", "ĠPIN", ":", "ĠPO", "51", "12", "65", "77", "H", "ĠY", ".", "A", ".", "T", ":", "Ġ01", "Ġ11", "89", "44", ",", "Ġpark", "lands", "@", "j", "av", "ah", "ouse", "af", "rica", ".", "com", "Ġ240", "6", "ĠFred", "rick", "ĠT", "b", "]", "Ġ72", "/", "1", "ĠCh", "k", "Ġ18", "28", "ĠG", "st", "Ġ11", "Jan", "'", "20", "Ġ10", ":", "04", "Ġ1", "ĠO", "atmeal", "ĠHalf", "Ġ1", "ĠSpark", "ĠWater", "Ġ0", ".", "5", "L", "Ġ190", ".", "00", "ĠFood", "Ġ220", ".", "00", "ĠBever", "age", "Ġ190", ".", "00", "Ġ10", ":", "48", "ĠTotal", "Ġ410", ".", "00", "Ġ16", "%", "ĠVAT", "Ġ55", ".", "99", "ĠBU", "Y", "ĠGOOD", "S", ":", "7", "17", "Ġ6", "43", "ĠHOW", "ĠWAS", "ĠYOUR", "ĠJ", "AV", "A", "ĠEX", "PER", "IENCE", "ĠTODAY", "?", "ĠTEXT", "ĠâĢ", "ĺ", "ĠJ", "AV", "A", "âĢ", "Ļ", "ĠTO", "Ġ07", "19", "Ġ50", "Ġ50", "Ġ50", ".", "ĠTHANK", "ĠYOU", ",", "ĠW", "EL", "COM", "E", "ĠAGA", "IN", ".", "ĠScan", "Ġto", "ĠPay", "ĠH", "ith", "ĠMP", "ESA"], "company_name": "NAIROBI JAVA HOUSE LTD. JAVA PARKLANDS", "receipt_date": null, "total_amount": 410.0, "receipt_address": "P.O BOX 21533 - 00505"}	2025-11-20 00:02:48.94446	2025-11-20 02:02:48.967101
b3e2b198-ed07-4823-8b78-b8bf06959da0	4526d57b-07d2-4fa1-9d61-f9d4d03970c8	test6.jpg	./uploads/receipts/b3e2b198-ed07-4823-8b78-b8bf06959da0.jpg	35801	image/jpeg	completed	2025-11-20 00:04:54.531603	2025-11-20 00:04:57.890332	\N	\N	\N		6450.00	KES	0.97	0.97	0.97	0.97	0.97	{"currency": "KES", "raw_text": " CELL. 0753 761 449 PIN NO. POS1152099 YAT NO. 01302295% E7101 Steve H Tol SB/t Chk 4784 Gat g FEB OtApr 18 14545 EAT IN } 1 Nyaté: Wings 1050.00 1 Pork Belly 1050.09 1 pravn calamari 1950.00 1 red Lanb curry 1850.00 500 ese i300 Food 5900.00 Beverage 550.00 Total ue 6450.00", "confidence": 0.9705921771391383, "raw_labels": ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "B-total", "B-total", "B-total", "B-total"], "raw_tokens": ["ĠCE", "LL", ".", "Ġ0", "753", "Ġ7", "61", "Ġ4", "49", "ĠPIN", "ĠNO", ".", "ĠPOS", "115", "20", "99", "ĠY", "AT", "ĠNO", ".", "Ġ01", "30", "22", "95", "%", "ĠE", "71", "01", "ĠSteve", "ĠH", "ĠTol", "ĠSB", "/", "t", "ĠCh", "k", "Ġ4", "784", "ĠGat", "Ġg", "ĠFE", "B", "ĠOt", "Apr", "Ġ18", "Ġ145", "45", "ĠE", "AT", "ĠIN", "Ġ}", "Ġ1", "ĠNy", "at", "Ã©", ":", "ĠWings", "Ġ1050", ".", "00", "Ġ1", "ĠPork", "ĠB", "elly", "Ġ1050", ".", "09", "Ġ1", "Ġp", "rav", "n", "Ġcalam", "ari", "Ġ1950", ".", "00", "Ġ1", "Ġred", "ĠLan", "b", "Ġcurry", "Ġ1850", ".", "00", "Ġ500", "Ġes", "e", "Ġi", "300", "ĠFood", "Ġ59", "00", ".", "00", "ĠBever", "age", "Ġ550", ".", "00", "ĠTotal", "Ġu", "e", "Ġ64", "50", ".", "00"], "company_name": "", "receipt_date": null, "total_amount": 6450.0, "receipt_address": ""}	2025-11-20 00:04:54.531586	2025-11-20 02:04:54.540116
ec5565a6-1c88-4fed-9241-0b20bd109653	4526d57b-07d2-4fa1-9d61-f9d4d03970c8	test2.jpg	./uploads/receipts/ec5565a6-1c88-4fed-9241-0b20bd109653.jpg	165293	image/jpeg	completed	2025-11-20 00:08:10.049234	2025-11-20 00:08:14.859857	\N	NATVAS LTDESTLANDS BRANCH	2815-11-17		2132779.00	KES	0.95	0.95	0.95	0.95	0.95	{"currency": "KES", "raw_text": " NATVAS LTD ___WESTLANDS BRANCH _ P.0.BOX 61608-80188 NATROBI TEL }828-2132779 FAX:020-2132 28 ~~ P/69852886/08444D IAT we 316 90086 USER: Cash Sale # 288 02108072665 Till No: 28-82 DateTime:11/17/2815 4:27:19 PM Store:28 ITEM QTY PRICE AMOUNT 44807376 4 x 15.00 ) FRESH FRUITY C/GUM 12 S 45.00 A 50000102 1 x 55,00 : EVEREADY BATT AAA 1812 2PACK 55.00 A TOTAL 7a.aea CASH 4,000.00 930, 80 CHANGE VAT ANT", "confidence": 0.9481844719160687, "raw_labels": ["B-company", "B-company", "I-company", "I-company", "O", "O", "I-company", "I-company", "I-company", "I-company", "I-company", "I-company", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O"], "raw_tokens": ["ĠNAT", "V", "AS", "ĠLTD", "Ġ___", "W", "EST", "LAN", "DS", "ĠBR", "AN", "CH", "Ġ_", "ĠP", ".", "0", ".", "BOX", "Ġ6", "16", "08", "-", "801", "88", "ĠNAT", "RO", "BI", "ĠT", "EL", "Ġ}", "8", "28", "-", "213", "27", "79", "ĠFA", "X", ":", "020", "-", "2", "132", "Ġ28", "Ġ", "~~", "ĠP", "/", "69", "85", "28", "86", "/", "08", "444", "D", "ĠI", "AT", "Ġwe", "Ġ316", "Ġ900", "86", "ĠUS", "ER", ":", "ĠCash", "ĠSale", "Ġ#", "Ġ288", "Ġ02", "1080", "7", "26", "65", "ĠTill", "ĠNo", ":", "Ġ28", "-", "82", "ĠDate", "Time", ":", "11", "/", "17", "/", "28", "15", "Ġ4", ":", "27", ":", "19", "ĠPM", "ĠStore", ":", "28", "ĠIT", "EM", "ĠQ", "TY", "ĠPR", "ICE", "ĠAM", "OUNT", "Ġ44", "807", "376", "Ġ4", "Ġx", "Ġ15", ".", "00", "Ġ)", "ĠFR", "ESH", "ĠFR", "U", "ITY", "ĠC", "/", "G", "UM", "Ġ12", "ĠS", "Ġ45", ".", "00", "ĠA", "Ġ5", "0000", "102", "Ġ1", "Ġx", "Ġ55", ",", "00", "Ġ:", "ĠEVER", "E", "AD", "Y", "ĠB", "ATT", "ĠAAA", "Ġ18", "12", "Ġ2", "P", "ACK", "Ġ55", ".", "00", "ĠA", "ĠTOTAL", "Ġ7", "a", ".", "aea", "ĠC", "ASH", "Ġ4", ",", "000", ".", "00", "Ġ9", "30", ",", "Ġ80", "ĠCH", "ANGE", "ĠVAT", "ĠAN", "T"], "company_name": "NATVAS LTDESTLANDS BRANCH", "receipt_date": "2815-11-17", "total_amount": 2132779.0, "receipt_address": ""}	2025-11-20 00:08:10.049225	2025-11-20 02:08:10.058976
a8891ad4-3f88-4558-ba71-4b225dfb1f25	367bed7a-a977-46a1-a00d-6b4daa05c688	test5.jpeg	./uploads/receipts/a8891ad4-3f88-4558-ba71-4b225dfb1f25.jpeg	101140	image/jpeg	completed	2025-11-23 20:32:10.789804	2025-11-23 20:32:14.46913	\N	NAIROBI JAVA HOUSE LTD. JAVA PARKLANDS	\N	P.O BOX 21533 - 00505	410.00	KES	0.97	0.97	0.97	0.97	0.97	{"currency": "KES", "raw_text": " NAIROBI JAVA HOUSE LTD. JAVA PARKLANDS P.O BOX 21533 - 00505 0740 048 896 PIN: PO51126577H V.A.T: 01 118944, Parklands@javahouseafrica.com 2406 Fredrick Tbl 72/1 Chk 1828 Gst 11Jan'20 10:04 1 Oatmeal Half 1 Spark Water 0.5L 190.00 Food 220.00 Beverage 190.00 10:48 Total 410.00 16% VAT 55.09 BUY GOODS:717 643 HOW WAS YOUR JAVA EXPERIENCE TODAY? TEXT ‘ JAVA’ TO 0719 50 SO 50. THANK YOU, WELCOME AGAIN. Scan to Pay Hith MPESA", "confidence": 0.968826369678273, "raw_labels": ["B-company", "B-company", "I-company", "I-company", "I-company", "I-company", "I-company", "I-company", "I-company", "B-company", "I-company", "I-company", "I-company", "I-company", "I-company", "B-address", "B-address", "I-address", "I-address", "I-address", "I-address", "I-address", "I-address", "I-address", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "B-total", "B-total", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O"], "raw_tokens": ["ĠNA", "IRO", "BI", "ĠJ", "AV", "A", "ĠHOUSE", "ĠLTD", ".", "ĠJ", "AV", "A", "ĠPARK", "LAN", "DS", "ĠP", ".", "O", "ĠBOX", "Ġ215", "33", "Ġ-", "Ġ00", "505", "Ġ07", "40", "Ġ0", "48", "Ġ8", "96", "ĠPIN", ":", "ĠPO", "51", "12", "65", "77", "H", "ĠV", ".", "A", ".", "T", ":", "Ġ01", "Ġ11", "89", "44", ",", "ĠPark", "lands", "@", "j", "av", "ah", "ouse", "af", "rica", ".", "com", "Ġ240", "6", "ĠFred", "rick", "ĠT", "bl", "Ġ72", "/", "1", "ĠCh", "k", "Ġ18", "28", "ĠG", "st", "Ġ11", "Jan", "'", "20", "Ġ10", ":", "04", "Ġ1", "ĠO", "atmeal", "ĠHalf", "Ġ1", "ĠSpark", "ĠWater", "Ġ0", ".", "5", "L", "Ġ190", ".", "00", "ĠFood", "Ġ220", ".", "00", "ĠBever", "age", "Ġ190", ".", "00", "Ġ10", ":", "48", "ĠTotal", "Ġ410", ".", "00", "Ġ16", "%", "ĠVAT", "Ġ55", ".", "09", "ĠBU", "Y", "ĠGOOD", "S", ":", "7", "17", "Ġ6", "43", "ĠHOW", "ĠWAS", "ĠYOUR", "ĠJ", "AV", "A", "ĠEX", "PER", "IENCE", "ĠTODAY", "?", "ĠTEXT", "ĠâĢ", "ĺ", "ĠJ", "AV", "A", "âĢ", "Ļ", "ĠTO", "Ġ07", "19", "Ġ50", "ĠSO", "Ġ50", ".", "ĠTHANK", "ĠYOU", ",", "ĠW", "EL", "COM", "E", "ĠAGA", "IN", ".", "ĠScan", "Ġto", "ĠPay", "ĠH", "ith", "ĠMP", "ESA"], "company_name": "NAIROBI JAVA HOUSE LTD. JAVA PARKLANDS", "receipt_date": null, "total_amount": 410.0, "receipt_address": "P.O BOX 21533 - 00505"}	2025-11-23 20:32:10.789801	2025-11-23 22:32:10.809022
b6cb43fc-e64b-4aa8-b4ac-c239c6bbbca4	08241ece-9426-47f4-b879-4898cd637f87	test6.jpg	./uploads/receipts/b6cb43fc-e64b-4aa8-b4ac-c239c6bbbca4.jpg	35801	image/jpeg	completed	2025-11-23 21:47:39.11209	2025-11-23 21:47:42.282122	\N	\N	\N		6450.00	KES	0.96	0.96	0.96	0.96	0.96	{"currency": "KES", "raw_text": " CELL. 0753 761 449, PIN NO. POS11520996 YAT NO. 01302295K. 101 Steve 4 Tol SB/t Chk 4784 Gat FEB OtApr 18 14345 EAT IN 41 Nyati Wings 1050.00 1 Pork Belly 1050.00 1 pravn calamari 1950.00 1 red Lanb curry 1850.00 1 Mango Juice 400.00, 1 Coke 150.00 Food 5900.00 Beverage 550.00 Total ue 6450.00", "confidence": 0.9599724135615609, "raw_labels": ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "B-total", "B-total", "B-total", "B-total"], "raw_tokens": ["ĠCE", "LL", ".", "Ġ0", "753", "Ġ7", "61", "Ġ4", "49", ",", "ĠPIN", "ĠNO", ".", "ĠPOS", "115", "20", "996", "ĠY", "AT", "ĠNO", ".", "Ġ01", "30", "22", "95", "K", ".", "Ġ101", "ĠSteve", "Ġ4", "ĠTol", "ĠSB", "/", "t", "ĠCh", "k", "Ġ4", "784", "ĠGat", "ĠFE", "B", "ĠOt", "Apr", "Ġ18", "Ġ143", "45", "ĠE", "AT", "ĠIN", "Ġ41", "ĠNy", "ati", "ĠWings", "Ġ1050", ".", "00", "Ġ1", "ĠPork", "ĠB", "elly", "Ġ1050", ".", "00", "Ġ1", "Ġp", "rav", "n", "Ġcalam", "ari", "Ġ1950", ".", "00", "Ġ1", "Ġred", "ĠLan", "b", "Ġcurry", "Ġ1850", ".", "00", "Ġ1", "ĠM", "ango", "ĠJuice", "Ġ400", ".", "00", ",", "Ġ1", "ĠCoke", "Ġ150", ".", "00", "ĠFood", "Ġ59", "00", ".", "00", "ĠBever", "age", "Ġ550", ".", "00", "ĠTotal", "Ġu", "e", "Ġ64", "50", ".", "00"], "company_name": "", "receipt_date": null, "total_amount": 6450.0, "receipt_address": ""}	2025-11-23 21:47:39.112084	2025-11-23 23:47:39.162187
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: macbook
--

COPY public.users (id, email, password_hash, full_name, phone_number, national_id, kyc_status, kyc_score, verification_date, account_type, is_active, created_at, updated_at, last_login) FROM stdin;
425c68c8-e693-43f1-a8f9-fce50aad5f38	user4@example.com	$2b$12$huGhLSdEm5K1QXZpU7XZnO5xBSn59a2zT.s1vU.umKsx2zVFmDRra	User	0712345678	12345678	pending	53.71	\N	investor	t	2025-11-19 14:33:59.970929	2025-11-19 17:57:54.610558	2025-11-19 15:57:55.06506
4526d57b-07d2-4fa1-9d61-f9d4d03970c8	user5@example.com	$2b$12$uU70wKFfOgjOHoXdwqN6TOenLG.qCY7kv1syt5HYC7R1NrFw0MDnS	user5	0712345678	12345678	pending	34.98	\N	investor	t	2025-11-19 17:59:43.815443	2025-11-20 02:07:30.378077	2025-11-20 00:07:30.85556
367bed7a-a977-46a1-a00d-6b4daa05c688	test2@example.com	$2b$12$8PBwTMcwG8kVtZa3Sthvt.yyh0WzUkNBqu8Mc1FwUBfJ87gYvSjVq	tester 2	12345678	12345678	pending	34.98	\N	investor	t	2025-11-23 22:29:57.214455	2025-11-23 22:32:14.541881	2025-11-23 20:31:27.143443
08241ece-9426-47f4-b879-4898cd637f87	sifakaveza@gmail.com	$2b$12$dWCB2/H0Wm9Q1JV5T/oyMuXWt..K6UGyNMdBA4m9f4llxUJ3thH2q	Sifa Mwachoni	0743251659	09553214	pending	34.98	\N	investor	t	2025-11-23 23:46:05.548144	2025-11-25 01:36:26.738187	2025-11-24 23:36:27.121493
\.


--
-- Data for Name: verification_scores; Type: TABLE DATA; Schema: public; Owner: macbook
--

COPY public.verification_scores (id, user_id, document_quality_score, spending_pattern_score, consistency_score, diversity_score, final_score, is_verified, verification_threshold, total_receipts, total_spending, unique_companies, unique_locations, date_range_days, average_transaction_amount, calculated_at) FROM stdin;
87d2e1d2-d0fb-4bd4-b529-ce5d65f32cd7	425c68c8-e693-43f1-a8f9-fce50aad5f38	96.33	68.40	0.00	38.53	53.71	f	75.00	3	2139639.00	2	1	0	713213.00	2025-11-19 17:23:35.052696
e002eb65-da3d-4a6c-bf8d-d41a2d0dde94	4526d57b-07d2-4fa1-9d61-f9d4d03970c8	97.00	4.12	0.00	24.25	34.98	f	75.00	1	410.00	1	1	0	410.00	2025-11-20 00:08:14.874204
6987a1b7-0c65-456f-a2eb-fefd9a77323e	367bed7a-a977-46a1-a00d-6b4daa05c688	97.00	4.12	0.00	24.25	34.98	f	75.00	1	410.00	1	1	0	410.00	2025-11-23 22:32:14.513093
08fb1247-d2ae-4edb-bea7-7b74284b21c5	08241ece-9426-47f4-b879-4898cd637f87	97.00	4.12	0.00	24.25	34.98	f	75.00	1	410.00	1	1	0	410.00	2025-11-23 21:47:47.1908
\.


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: macbook
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: receipts receipts_pkey; Type: CONSTRAINT; Schema: public; Owner: macbook
--

ALTER TABLE ONLY public.receipts
    ADD CONSTRAINT receipts_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: macbook
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: verification_scores verification_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: macbook
--

ALTER TABLE ONLY public.verification_scores
    ADD CONSTRAINT verification_scores_pkey PRIMARY KEY (id);


--
-- Name: ix_audit_logs_action_type; Type: INDEX; Schema: public; Owner: macbook
--

CREATE INDEX ix_audit_logs_action_type ON public.audit_logs USING btree (action_type);


--
-- Name: ix_audit_logs_created_at; Type: INDEX; Schema: public; Owner: macbook
--

CREATE INDEX ix_audit_logs_created_at ON public.audit_logs USING btree (created_at);


--
-- Name: ix_audit_logs_user_id; Type: INDEX; Schema: public; Owner: macbook
--

CREATE INDEX ix_audit_logs_user_id ON public.audit_logs USING btree (user_id);


--
-- Name: ix_receipts_company_name; Type: INDEX; Schema: public; Owner: macbook
--

CREATE INDEX ix_receipts_company_name ON public.receipts USING btree (company_name);


--
-- Name: ix_receipts_status; Type: INDEX; Schema: public; Owner: macbook
--

CREATE INDEX ix_receipts_status ON public.receipts USING btree (status);


--
-- Name: ix_receipts_uploaded_at; Type: INDEX; Schema: public; Owner: macbook
--

CREATE INDEX ix_receipts_uploaded_at ON public.receipts USING btree (uploaded_at);


--
-- Name: ix_receipts_user_id; Type: INDEX; Schema: public; Owner: macbook
--

CREATE INDEX ix_receipts_user_id ON public.receipts USING btree (user_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: macbook
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_verification_scores_final_score; Type: INDEX; Schema: public; Owner: macbook
--

CREATE INDEX ix_verification_scores_final_score ON public.verification_scores USING btree (final_score);


--
-- Name: ix_verification_scores_user_id; Type: INDEX; Schema: public; Owner: macbook
--

CREATE UNIQUE INDEX ix_verification_scores_user_id ON public.verification_scores USING btree (user_id);


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: macbook
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: receipts receipts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: macbook
--

ALTER TABLE ONLY public.receipts
    ADD CONSTRAINT receipts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: verification_scores verification_scores_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: macbook
--

ALTER TABLE ONLY public.verification_scores
    ADD CONSTRAINT verification_scores_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT USAGE ON SCHEMA public TO kyc_user;


--
-- Name: TABLE audit_logs; Type: ACL; Schema: public; Owner: macbook
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.audit_logs TO kyc_user;


--
-- Name: TABLE receipts; Type: ACL; Schema: public; Owner: macbook
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.receipts TO kyc_user;


--
-- Name: TABLE users; Type: ACL; Schema: public; Owner: macbook
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.users TO kyc_user;


--
-- Name: TABLE verification_scores; Type: ACL; Schema: public; Owner: macbook
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.verification_scores TO kyc_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: macbook
--

ALTER DEFAULT PRIVILEGES FOR ROLE macbook IN SCHEMA public GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES  TO kyc_user;


--
-- PostgreSQL database dump complete
--

\unrestrict dmSiJ61Jppt0vPWqQUgccPaJwf9xfdFCOuAf6OT4KFjnkMHs4HLnmnMo3YZNGhy


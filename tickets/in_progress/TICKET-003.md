# API Key generation & middleware

## Metadata
* **Ticket ID:** TICKET-003
* **Status:** done
* **Priority:** high
* **Assigned to:** copilot
* **Created on:** 2023-11-27
* **Changed on:** 2023-11-28

## Description
Implement API key generation functionality and middleware for API key validation. This will allow external services to access the API without user-based authentication.

## Project Documentation References
* Database documentation: /docs/database/README.md and /docs/database/schema.md
* Product Requirements Document (PRD): /docs/PRD.md

## Implementation Details

### API Key Generation
1. Model ApiKey został już poprawnie zdefiniowany w app/models/user.py z wymaganymi polami:
   - id (primary key)
   - user_id (foreign key do tabeli users)
   - key_value (unikalny ciąg znaków klucza API)
   - description (opcjonalny opis klucza API)
   - last_used (timestamp ostatniego użycia klucza)
   - created_at (timestamp utworzenia klucza)
   - revoked (flaga określająca czy klucz został cofnięty)

2. Schematy ApiKeyCreate i ApiKeyResponse zostały zaktualizowane w app/schemas/user.py:
   - ApiKeyCreate: pole description (opcjonalne)
   - ApiKeyResponse: pola id, key_value, description, created_at

3. Implementacja funkcji generowania kluczy API w app/api/auth.py:
   - POST /api/auth/apikey/generate endpoint
   - Generowanie bezpiecznego losowego klucza API
   - Przechowywanie klucza API w bazie danych z powiązaniem do użytkownika
   - Zwracanie klucza API do klienta

4. Implementacja funkcji cofania kluczy API:
   - POST /api/auth/apikey/revoke/{key_id} endpoint
   - Oznaczanie klucza API jako cofniętego (revoked=True)
   - Weryfikacja, że użytkownik może cofnąć tylko swoje własne klucze API

### API Key Middleware
1. Middleware walidacji kluczy API:
   - Funkcja get_current_user_from_api_key ekstrahuje klucz API z nagłówka x-api-key
   - Weryfikacja klucza API w bazie danych
   - Sprawdzenie czy klucz nie został cofnięty
   - Przypisanie użytkownika do żądania
   - Zwrócenie błędu 401 Unauthorized jeśli klucz jest nieprawidłowy/cofnięty

2. Aktualizacja przepływu uwierzytelniania:
   - Funkcja get_current_user najpierw sprawdza token JWT w nagłówku Authorization
   - Jeśli nie ma ważnego tokena JWT, sprawdza klucz API w nagłówku x-api-key
   - Zwraca błąd 401 Unauthorized jeśli obie metody uwierzytelniania zawiodą

3. Endpoint do pobierania informacji o zalogowanym użytkowniku:
   - GET /api/users/me zwraca dane użytkownika dla obu metod uwierzytelniania

### Implementacja testów
1. Testy jednostkowe:
   - Testy generowania kluczy API
   - Testy walidacji kluczy API
   - Testy cofania kluczy API
   - Testy middleware uwierzytelniania z kluczami API
   - Testy obsługi błędów

2. Testy E2E:
   - Testy logowania użytkownika i generowania klucza API
   - Testy dostępu do endpointów API przy użyciu uwierzytelniania kluczem API
   - Testy cofania klucza API i następującej po tym nieudanej próby uwierzytelnienia

## Tasks
- [x] Implement POST /api/auth/apikey/generate endpoint
  - [x] Add route and controller function
  - [x] Generate unique API key
  - [x] Store API key in database
  - [x] Return API key to user
- [x] Implement API key middleware
  - [x] Extract API key from header
  - [x] Validate API key against database
  - [x] Check if key is revoked
  - [x] Associate request with user
  - [x] Return 401 if invalid
- [x] Write tests
  - [x] Test as much as possible with unit tests
  - [x] Test all endpoints with e2e tests
- [x] Update documentation
  - [x] Add OpenAPI documentation for the endpoint
  - [x] Document API key usage
- [x] Update project changelog

## Changelog
### [2023-11-27 14:00] - Ticket created
Initial ticket creation for API Key generation and middleware functionality.

### [2023-11-28 09:00] - Ticket moved to in_progress
- Updated status to in_progress
- Added detailed implementation plan

### [2023-11-28 14:00] - Implementation completed
- Created unit tests for API key generation and middleware
- Implemented API key generation endpoint
- Implemented API key middleware for authentication
- Created API key revocation endpoint
- Added E2E tests for API key authentication
- Updated OpenAPI documentation for API key endpoints

### [2023-11-28 16:00] - Ticket completed
- All tasks have been completed
- All tests pass successfully
- Moved ticket to done status

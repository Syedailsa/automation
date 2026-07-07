#!/usr/bin/env bash
# Integration test script for NotebookLM Portal API
# Run: bash tests/integration_test.sh

set -e

BASE_URL="http://localhost:8000"
PASS=0
FAIL=0

run_test() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local expected_code="$4"
    local data="$5"

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint" 2>/dev/null)
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL$endpoint" 2>/dev/null)
    fi

    http_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "$expected_code" ]; then
        echo "  ✓ $name (HTTP $http_code)"
        PASS=$((PASS + 1))
    else
        echo "  ✗ $name (expected $expected_code, got $http_code)"
        echo "    Response: $body"
        FAIL=$((FAIL + 1))
    fi
}

echo "==================================="
echo " NotebookLM Portal API Tests"
echo "==================================="
echo ""

echo "--- Health Check ---"
run_test "Health endpoint" "GET" "/api/health" "200"
echo ""

echo "--- Auth Routes ---"
run_test "Google redirect" "GET" "/api/auth/google/redirect" "200"
run_test "Google callback invalid" "POST" "/api/auth/google/callback" "400" '{"code":"bad_code"}'
run_test "Get me unauthorized" "GET" "/api/auth/me" "401"
run_test "Logout unauthorized" "POST" "/api/auth/logout" "401"
echo ""

echo "--- Notebook Routes (unauthorized) ---"
run_test "List notebooks unauth" "GET" "/api/notebooks" "401"
run_test "Create notebook unauth" "POST" "/api/notebooks" "401" '{"title":"Test"}'
run_test "Get notebook invalid id" "GET" "/api/notebooks/not-a-uuid" "422"
echo ""

echo "--- Source Routes (unauthorized) ---"
run_test "Add source unauth" "POST" "/api/notebooks/00000000-0000-0000-0000-000000000000/sources/url" "401" '{"title":"Test","url":"https://example.com"}'
echo ""

echo "--- Output Routes (unauthorized) ---"
run_test "Delete output unauth" "DELETE" "/api/outputs/00000000-0000-0000-0000-000000000000" "401"
echo ""

echo "--- Agent Routes (unauthorized) ---"
run_test "Refine input unauth" "POST" "/api/agent/refine" "401" '{"input_text":"Hello"}'
run_test "Execute workflow unauth" "POST" "/api/agent/execute" "401" '{"input_text":"Test"}'
run_test "Get status unauth" "GET" "/api/agent/status/test-id" "401"
run_test "Get history unauth" "GET" "/api/agent/history" "401"
echo ""

echo "--- WebSocket ---"
run_test "WS endpoint available" "GET" "/ws" "426"
echo ""

echo "==================================="
echo " Results: $PASS passed, $FAIL failed"
echo "==================================="

if [ $FAIL -gt 0 ]; then
    exit 1
fi

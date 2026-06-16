package com.example.aicommerce;

import org.junit.jupiter.api.Test;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

class PermissionIntegrationTest extends AbstractIntegrationTest {

    @Test
    void anonymousCanBrowseProductsButCannotAccessAdminApis() throws Exception {
        mockMvc.perform(get("/api/products"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0));

        mockMvc.perform(get("/api/admin/products"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.code").value(401));
    }

    @Test
    void normalUserCannotAccessAdminApis() throws Exception {
        String token = loginToken("user", "user123");

        mockMvc.perform(get("/api/admin/products")
                        .header("Authorization", bearer(token)))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.code").value(403));
    }

    @Test
    void operatorAndAdminCanAccessAdminApis() throws Exception {
        String operatorToken = loginToken("operator", "operator123");
        String adminToken = loginToken("admin", "admin123");

        mockMvc.perform(get("/api/admin/products")
                        .header("Authorization", bearer(operatorToken)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0));

        mockMvc.perform(get("/api/admin/orders")
                        .header("Authorization", bearer(adminToken)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0));
    }
}

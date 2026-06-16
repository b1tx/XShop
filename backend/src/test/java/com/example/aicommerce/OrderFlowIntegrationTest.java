package com.example.aicommerce;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MvcResult;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

class OrderFlowIntegrationTest extends AbstractIntegrationTest {

    @Test
    void userCanCreatePayShipAndReceiveOrder() throws Exception {
        String userToken = loginToken("user", "user123");
        String adminToken = loginToken("admin", "admin123");

        Long cartItemId = addCartItem(userToken, 3001L, 2);
        Long orderId = createOrder(userToken, cartItemId);

        mockMvc.perform(post("/api/orders/" + orderId + "/pay")
                        .header("Authorization", bearer(userToken)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.status").value("PAID"));

        mockMvc.perform(put("/api/admin/orders/" + orderId + "/ship")
                        .header("Authorization", bearer(adminToken)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.status").value("SHIPPED"));

        mockMvc.perform(post("/api/orders/" + orderId + "/receive")
                        .header("Authorization", bearer(userToken)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.status").value("RECEIVED"));

        String status = jdbcTemplate.queryForObject("select status from order_main where id = ?", String.class, orderId);
        Integer paymentCount = jdbcTemplate.queryForObject("select count(*) from payment_record where order_id = ?", Integer.class, orderId);
        assertThat(status).isEqualTo("RECEIVED");
        assertThat(paymentCount).isEqualTo(1);
    }

    private Long addCartItem(String token, Long productId, int quantity) throws Exception {
        MvcResult result = mockMvc.perform(post("/api/cart/items")
                        .header("Authorization", bearer(token))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"productId\":" + productId + ",\"quantity\":" + quantity + "}"))
                .andExpect(status().isOk())
                .andReturn();
        return json(result).path("data").path("id").asLong();
    }

    private Long createOrder(String token, Long cartItemId) throws Exception {
        String body = "{\"cartItemIds\":[" + cartItemId + "],\"receiverName\":\"测试用户\",\"receiverPhone\":\"13800000000\",\"receiverAddress\":\"测试地址\"}";
        MvcResult result = mockMvc.perform(post("/api/orders")
                        .header("Authorization", bearer(token))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.status").value("CREATED"))
                .andReturn();
        JsonNode data = json(result).path("data");
        return data.path("id").asLong();
    }
}

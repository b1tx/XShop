package com.example.aicommerce;

import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MvcResult;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

class InventoryConsistencyIntegrationTest extends AbstractIntegrationTest {

    @Test
    void createOrderDeductsStockAndCancelRestoresStockWithInventoryRecords() throws Exception {
        String userToken = loginToken("user", "user123");
        int beforeStock = stockOf(3001L);

        Long cartItemId = addCartItem(userToken, 3001L, 3);
        Long orderId = createOrder(userToken, cartItemId);

        assertThat(stockOf(3001L)).isEqualTo(beforeStock - 3);
        assertInventoryRecord(orderId, 3001L, "ORDER_CREATE", -3, beforeStock, beforeStock - 3);

        mockMvc.perform(post("/api/orders/" + orderId + "/cancel")
                        .header("Authorization", bearer(userToken)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.status").value("CANCELLED"));

        assertThat(stockOf(3001L)).isEqualTo(beforeStock);
        assertInventoryRecord(orderId, 3001L, "ORDER_CANCEL", 3, beforeStock - 3, beforeStock);
    }

    @Test
    void insufficientStockDoesNotCreateDirtyOrderOrChangeStock() throws Exception {
        String userToken = loginToken("user", "user123");
        int beforeStock = stockOf(3002L);

        Long cartItemId = addCartItem(userToken, 3002L, 2);
        Integer beforeOrderCount = jdbcTemplate.queryForObject("select count(*) from order_main", Integer.class);

        mockMvc.perform(post("/api/orders")
                        .header("Authorization", bearer(userToken))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"cartItemIds\":[" + cartItemId + "],\"receiverName\":\"测试用户\",\"receiverPhone\":\"13800000000\",\"receiverAddress\":\"测试地址\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(400));

        Integer afterOrderCount = jdbcTemplate.queryForObject("select count(*) from order_main", Integer.class);
        assertThat(stockOf(3002L)).isEqualTo(beforeStock);
        assertThat(afterOrderCount).isEqualTo(beforeOrderCount);
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
        MvcResult result = mockMvc.perform(post("/api/orders")
                        .header("Authorization", bearer(token))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"cartItemIds\":[" + cartItemId + "],\"receiverName\":\"测试用户\",\"receiverPhone\":\"13800000000\",\"receiverAddress\":\"测试地址\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.status").value("CREATED"))
                .andReturn();
        return json(result).path("data").path("id").asLong();
    }

    private int stockOf(Long productId) {
        return jdbcTemplate.queryForObject("select stock from product where id = ?", Integer.class, productId);
    }

    private void assertInventoryRecord(Long orderId, Long productId, String businessType, int changeQuantity, int beforeStock, int afterStock) {
        Integer count = jdbcTemplate.queryForObject(
                "select count(*) from inventory_record where business_id = ? and product_id = ? and business_type = ? and change_quantity = ? and before_stock = ? and after_stock = ?",
                Integer.class,
                orderId,
                productId,
                businessType,
                changeQuantity,
                beforeStock,
                afterStock
        );
        assertThat(count).isEqualTo(1);
    }
}

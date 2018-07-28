SELECT *, (min_price*batch_size_formula)-(single_unit_cost*batch_size_formula) margin_comp_immediate,
          (price_avg_week*batch_size_formula)-(single_unit_cost*batch_size_formula) margin_comp_weekly
FROM ( SELECT
             pa.id,
             ur.id user_id,
             ei.id item_id,
             tu.id trade_hub_id,
             re.name region_name,
             tu.name trade_hub_name,
             ei.name item_name,
             single_unit_cost,
             min_price,
             price_avg_week,
             vol_month,
             history_volume,
             full_batch_size,
             daily_monthly_pcent,
             margin_percent,
             CASE
               WHEN batch_cap
                       THEN LEAST(full_batch_size, FLOOR(history_volume * vol_month_pcent * 0.01))
               ELSE FLOOR(history_volume * vol_month_pcent * 0.01)
                 END batch_size_formula,
              min_amount_for_advice,
              min_pcent_for_advice * 0.01 min_pcent_for_advice
      FROM prices_advices pa
             JOIN eve_items ei ON pa.eve_item_id = ei.id
             JOIN trade_hubs tu ON pa.trade_hub_id = tu.id
             JOIN regions re ON re.id = tu.region_id
             JOIN trade_hubs_users thu ON thu.trade_hub_id = pa.trade_hub_id
             JOIN eve_items_users eiu ON eiu.eve_item_id = pa.eve_item_id
             JOIN users ur ON thu.user_id = ur.id
             WHERE history_volume IS NOT NULL
             AND ur.id = eiu.user_id
) prices_advices_sub_1

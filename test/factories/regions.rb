FactoryBot.define do

  factory :region do

    cpp_region_id '123456'
    name 'Region test'

    factory :heimatar do
      cpp_region_id '10000030'
      name 'Heimatar'

      after(:create) do |region|

        pator = create( :rens, region: region )
        rens = create( :pator, region: region )

        blueprint_and_market_group = create( :inferno_fury_cruise_missile )
        blueprint_but_no_market_group = create( :mjolnir_fury_cruise_missile )
        no_market_group_and_no_blueprint = create( :inferno_precision_cruise_missile )

        [ blueprint_and_market_group, blueprint_but_no_market_group, no_market_group_and_no_blueprint ].each do |item|

          [ pator, rens ].each do |trade_hub|
            create( :min_price, trade_hub: trade_hub, eve_item: item )
          end

          create( :crest_prices_last_month_average, eve_item: item, region: region )

        end
      end

    end

    # A region where we have no crest data. If we pass items: EveItem.all to create( :domain )
    # Then the evaluator.items loop will create data for each items (EveItem.all or any other item array you give as an argument)
    factory :domain do
      cpp_region_id '10000043'
      name 'Domain'

      transient do
        items { [] }
      end

      after(:create) do |region, evaluator|

        amarr = create( :amarr, region: region )

        evaluator.items.each do |item|

          [ amarr ].each do |trade_hub|
            create( :min_price, trade_hub: trade_hub, eve_item: item )
          end

          # create( :crest_prices_last_month_average, eve_item: item, region: region )

        end
      end

    end

  end

end

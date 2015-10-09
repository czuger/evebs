FactoryGirl.define do

  factory :region do

    factory :heimatar do
      cpp_region_id '10000030'
      name 'Heimatar'

      after(:create) do |region|

        pator = create( :rens, region: region )
        rens = create( :pator, region: region )

        inferno = create( :inferno_fury_cruise_missile )
        mjolnir = create( :mjolnir_fury_cruise_missile )

        [ inferno, mjolnir ].each do |item|

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

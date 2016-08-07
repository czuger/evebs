require 'set'

module Setup::UpdateMarketGroups

  # This is the right eve item update. It rely on the files downloaded from CPP
  def update_market_groups

    puts 'Checking market groups' unless Rails.env == 'test'
    break_on_tests_counter = 0
    Setup::CppSourcesMarketGroup.pluck( :marketGroupID ).each do |id|
      add_cpp_market_group_id( id ) unless MarketGroup.find_by_cpp_market_group_id( id )
      break_on_tests_counter += 1
      break if Rails.env=='test' && break_on_tests_counter > 0
    end

  end

  def add_cpp_market_group_id( cpp_market_group_id )
    # Get the market
    market_group = Setup::CppSourcesMarketGroup.find_by_marketGroupID( cpp_market_group_id )
    raise "Unable to find market for cpp_market_group_id #{cpp_market_group_id}" unless market_group
    puts "About to create #{market_group.inspect}" unless Rails.env == 'test'

    # Ensure the parent has been created
    if market_group.parentGroupID
      parent_market_group = Setup::CppSourcesMarketGroup.find_by_marketGroupID( market_group.parentGroupID )
      unless parent_market_group
        puts "Adding parent for #{market_group.inspect}" unless Rails.env == 'test'
        parent_market_group = add_cpp_market_group_id( market_group.parentGroupID )
      end
    end

    MarketGroup.create!(
      cpp_market_group_id: market_group.marketGroupID, parent_id: ( parent_market_group.id if parent_market_group ),
      name: market_group.marketGroupName )
  end
end
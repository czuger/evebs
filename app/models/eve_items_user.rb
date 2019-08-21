class EveItemsUser < ApplicationRecord

  # Usefull for tests. In console type
  # EveItemsUser.select_all( user_id )
  # user_id is the id of your user
  def self.select_all( user_id )
    ActiveRecord::Base.transaction do
      EveItemsUser.where( user_id: user_id ).delete_all

      EveItem.where.not( blueprint_id: nil ).where( faction: false ).pluck( :id ).in_groups_of( 500 ).each do |g|
        links = []
        g.each do |eve_item_id|
          links << EveItemsUser.new( user_id: user_id, eve_item_id: eve_item_id, )
        end
        EveItemsUser.import( links )
      end
    end
  end

end
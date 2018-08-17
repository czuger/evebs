class RemoveUserPlShareIdFromUser < ActiveRecord::Migration[5.2]
  def change
    remove_column :users, :user_pl_share_id
  end
end

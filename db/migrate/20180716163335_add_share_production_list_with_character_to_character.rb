class AddShareProductionListWithCharacterToCharacter < ActiveRecord::Migration[5.2]
  def change
    add_column :characters, :character_pl_share_id, :bigint
    add_index :characters, :character_pl_share_id
    add_foreign_key :characters, :characters, column: :character_pl_share_id
  end
end

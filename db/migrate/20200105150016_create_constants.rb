class CreateConstants < ActiveRecord::Migration[5.2]
  def change
    create_table :constants do |t|
      t.string :libe, null: false, index: { unique: true }
      t.float :f_value
      t.string :description, null: false

      t.timestamps
    end
  end
end

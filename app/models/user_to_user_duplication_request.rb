class UserToUserDuplicationRequest < ApplicationRecord

  SALES_ORDERS = 1

  belongs_to :sender, class_name: 'User'

end

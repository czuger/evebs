FactoryBot.define do
  factory :crontab do
    cron_name {'MyString'}
    status {false}
  end
end

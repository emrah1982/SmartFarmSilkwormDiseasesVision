# Geliştirme Kuralları

Bu projede katmanlı mimariye uygun, modüler ve test edilebilir bir yapı hedeflenir.

## İlkeler

- SOLID prensiplerine uyum
- Temiz kod (Clean Code)
- Bağımlılıkların açıkça enjekte edilmesi (Dependency Injection)
- Domain katmanının bağımsızlığı (harici kütüphane yok)
- Hata yakalama ve güvenli düşüş (graceful fallback)

## Katman Sınırları

- Presentation: Sadece görselleştirme ve çıktı üretimi. İş kuralı barındırmaz.
- Application: Akış/pipeline yönetimi. Domain ve Infrastructure'ı orkestre eder.
- Domain: Sadece iş kuralları ve modeller. Harici bağımlılık yok.
- Infrastructure: Model, veri kaynağı, I/O. Domain nesnelerini kullanabilir fakat Domain bu katmana bağımlı olmaz.

## Kod Stili

- Docstring ve anlamlı isimlendirme
- Fonksiyon/method uzunluklarını sınırlı tutun; tek sorumluluk
- 300–500 satırı geçen dosyaları parçalara bölün (modül ya da sınıf bazında)
- Yorumlar sadece “neden”leri açıklasın (ne yaptığını kod anlatmalı)

## Test

- Domain için birim testler zorunlu
- Application için sahte (fake) bağımlılıklarla smoke/integration testleri
- Infrastructure için çevresel bağımlılıklara toleranslı testler (opsiyonel)

## Hata Yönetimi ve Log

- Infrastructure’da try/except ile dış bağımlılık hatalarını yalıtın
- Hataları kullanıcıya uygun mesajla iletin; uygulama akışını tamamen durdurmayın

## Versiyonlama ve PR

- Küçük, odaklı PR’lar
- Test ve dokümantasyon güncellemesi eşlik etmeli
- Mimari değişikliklerde `docs/architecture.md` güncellensin

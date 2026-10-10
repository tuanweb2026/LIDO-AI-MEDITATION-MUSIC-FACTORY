#!/usr/bin/env python3
"""
Generate 100 Quotes on Vô Thường, Vô Ngã, Tánh Không & Render 3-Hour Draft Video
LIDO AI Meditation Music Factory
"""

import sys
import os
import json
import subprocess

QUOTES_100 = [
    # 1 - 35: VÔ THƯỜNG (Impermanence)
    "1. Tất cả pháp hữu vi đều là vô thường, có sinh tất có diệt. Tâm an nhiên khi chấp nhận sự đổi thay.",
    "2. Hoa nở rồi tàn, trăng tròn lại khuyết. Vô thường không phải u buồn, mà là bản chất của sự sống.",
    "3. Ngày hôm nay trôi qua sẽ không bao giờ trở lại. Hãy trân trọng từng phút giây trong tĩnh lặng.",
    "4. Đừng bám chấp vào quá khứ, đừng mong cầu ở tương lai. Hiện tại chính là nơi bình an nhất.",
    "5. Mọi dòng sông đều chảy ra biển lớn, mọi đám mây rồi sẽ tan biến trên tầng không.",
    "6. Thân thể này, cảm xúc này, ý nghĩ này... tất cả đều đang đổi thay từng khoảnh khắc.",
    "7. Khi thấu hiểu vô thường, ta ngừng oán trách những dở dang và biết mỉm cười với hiện tại.",
    "8. Cuộc đời như giọt sương trên đầu cỏ, tan biến khi ánh mặt trời vừa hửng sáng.",
    "9. Buông tay không phải là mất mát, mà là nhường chỗ cho sự thanh thản bước vào.",
    "10. Không có gì là vĩnh cửu dưới ánh mặt trời. Hãy sống chân thành và an an lặng lặng.",
    "11. Niềm vui đến rồi đi, nỗi buồn cũng sinh rồi diệt. Đừng để lòng mình chao đảo theo ngoại cảnh.",
    "12. Thảnh thơi bước đi trong vô thường, như làn gió mát lướt nhẹ qua rừng trúc.",
    "13. Khi biết trước tương phùng sẽ có ngày chia ly, ta càng nâng niu từng khoảnh khắc hiện hữu.",
    "14. Thế gian vạn vật như giấc mộng giữa ban ngày, thức tỉnh rồi chỉ còn lại lòng thanh thản.",
    "15. Vô thường nhắc nhở ta rằng không có khó khăn nào kéo dài mãi mãi.",
    "16. Hãy thả trôi những muộn phiền như chiếc lá khô trôi theo dòng suối mát.",
    "17. Đêm tối trôi qua, bình minh lại đến. Vô thường chính là niềm hy vọng của sự khởi đầu.",
    "18. Đừng giữ chặt những gì không thuộc về mình, vì vạn vật vốn là của đất trời.",
    "19. Nhẹ nhàng đi qua những biến động của cuộc đời với trái tim bao dung và thanh tịnh.",
    "20. Tâm tĩnh lặng nhìn đời đổi thay, như rặng núi đứng yên giữa ngàn mây trôi.",
    "21. Mọi vinh hoa phú quý rồi cũng như mây khói, chỉ có sự bình an nội tại là đáng quý.",
    "22. Cảm xúc như những làn sóng trên mặt biển, rồi sẽ dịu êm trả lại sự phẳng lặng.",
    "23. Học cách buông bỏ mỗi ngày là học cách trở về với sự tự do trọn vẹn.",
    "24. Khi ta không cưỡng lại sự đổi thay, mọi đau khổ liền tự động tan biến.",
    "25. Sức mạnh lớn nhất của tâm hồn là sự kiên định tĩnh lặng giữa muôn vàn vô thường.",
    "26. Mỗi hơi thở ra là một sự giải thoát, mỗi hơi thở vào là một sự tái sinh.",
    "27. Hãy sống trọn vẹn từng phút giây như thể đó là khoảnh khắc duy nhất trên đời.",
    "28. Cuộc đời là chuỗi những cuộc gặp gỡ và chia xa, hãy để tất cả diễn ra tự nhiên.",
    "29. Bình an không nằm ở hoàn cảnh bên ngoài, mà nằm ở thái độ đón nhận của tâm ta.",
    "30. Mây tan mây hợp trên tầng không, lòng không bận bận thế gian thong dong.",
    "31. Sự đổi thay là quy luật duy nhất không bao giờ đổi thay.",
    "32. Đừng xây nhà trên cát, đừng gửi gắm hạnh phúc vào những điều mong manh.",
    "33. Biết đủ là hạnh phúc lớn nhất, biết buông là tự do cao nhất.",
    "34. Nhẹ bước thong dong giữa cõi đời, tâm không vướng bận lòng an vui.",
    "35. Trôi theo dòng chảy của đất trời với trái tim ngập tràn yêu thương.",

    # 36 - 70: VÔ NGÃ (Non-Self / Anatta)
    "36. Cái 'tôi' chỉ là một ảo tưởng của tâm trí. Khi tan hòa vào vũ trụ, vạn vật là một.",
    "37. Sóng nước không thể tách rời khỏi đại dương. Ta và vạn vật vốn hòa quyện làm một.",
    "38. Đừng tìm kiếm cái 'tôi' trong những suy nghĩ, vì suy nghĩ chỉ là làn gió thoảng qua.",
    "39. Khi không còn cái 'tôi' để bảo vệ, nỗi sợ hãi và giận dữ tự nhiên biến mất.",
    "40. Như ngọn lửa chuyền từ cây nến này sang cây nến khác, sự sống là dòng chảy liên tục.",
    "41. Ta không sở hữu bất kỳ điều gì, kể cả thân xác này. Tất cả chỉ là duyên hợp.",
    "42. Khi lòng bớt ngạo mạn và bám chấp, sự yêu thương và thấu hiểu tự nhiên đong đầy.",
    "43. Hãy khiêm nhường như hạt bụi nhỏ, để thấy mình hòa hợp cùng cả không gian.",
    "44. Nỗi đau nảy sinh khi ta nghĩ 'đây là của tôi'. Buông xả sở hữu, tâm liền an tịnh.",
    "45. Thân này là sự kết hợp của đất, nước, gió, lửa. Khi hết duyên lại trở về cùng thiên nhiên.",
    "46. Hãy lắng nghe tiếng sáo vang mà không cần tìm kiếm người thổi sáo.",
    "47. Khi cái 'tôi' lắng xuống, sự chân thật và lòng từ bi tự nhiên tỏa sáng.",
    "48. Đừng để lòng mình bị giam cầm trong cái gông cúng của định kiến cá nhân.",
    "49. Hạnh phúc chân thật bừng nở khi ta quên đi bản thân để nâng đỡ người khác.",
    "50. Ta là cây trúc nghiêng mình trước gió, không kháng cự nên không bao giờ gãy.",
    "51. Cảnh vật tĩnh lặng hay xôn xao đều do tâm ta phân biệt mà ra.",
    "52. Nhìn cây thấy lá, nhìn lá thấy rừng. Mọi sự vật đều chứa đựng lẫn nhau.",
    "53. Khi buông bỏ ảo tưởng về một cái 'tôi' cố định, ta tìm thấy sự tự do đích thực.",
    "54. Giọt nước hòa vào biển cả sẽ không bao giờ cạn khô.",
    "55. Đừng so sánh mình với bất kỳ ai, vì vạn vật đều có vẻ đẹp riêng của nó.",
    "56. Tâm rộng lớn như lòng đại dương, chứa đựng mọi dòng sông mà không hề tràn dâng.",
    "57. Sự tĩnh lặng chân thật là khi cái 'tôi' không còn tranh giành đúng sai.",
    "58. Hãy như dòng suối trong vắt, chảy qua mọi ghềnh đá mà không hề vướng bận.",
    "59. Không bám chấp vào thành hay bại, khen hay chê. Lòng an nhiên như mây trời.",
    "60. Trái tim rộng mở là trái tim không dựng lên rào cản phân biệt.",
    "61. Khi ta không còn tự khẳng định mình, vạn vật tự nhiên tôn trọng ta.",
    "62. Nhẹ nhàng đi qua nhân thế, không để lại vết chân oán hận hay giận hường.",
    "63. Sống bình dị giữa đời thường, như hoa sen nở giữa hồ nước trong.",
    "64. Sự tha thứ lớn nhất là tha thứ cho những lầm lỗi của chính bản thân mình.",
    "65. Khi ta thương yêu người khác mà không đòi hỏi đền đáp, đó là tình thương vô ngã.",
    "66. Hãy nhìn cuộc đời bằng đôi mắt của sự bao dung và thấu hiểu.",
    "67. Cây không đòi hỏi đất trả ơn, sông không đòi hỏi biển ghi nhận.",
    "68. Tâm vô ngã là tâm không bị chao đảo trước phong ba bão táp của cuộc đời.",
    "69. Hãy chìm vào tĩnh lặng để nghe tiếng nói nhiệm màu của trái tim.",
    "70. Trở về với chính mình là trở về với sự an bình sẵn có.",

    # 71 - 100: TÁNH KHÔNG (Emptiness / Sunyata)
    "71. Tánh Không không phải là hư vô bế tắc, mà là khả năng vô tận của sự khởi sinh.",
    "72. Ly rỗng mới chứa được nước. Tâm rỗng rang mới đón nhận được sự an lành.",
    "73. Như bầu trời trong xanh chứa đựng muôn vàn đám mây mà không bị mây làm ô nhiễm.",
    "74. Bản chất của mọi sự vật là Không, nên vạn vật mới có thể biến đổi và phát triển.",
    "75. Khi tâm không vướng bận một hạt bụi, khắp nơi đều là chốn bồng lai.",
    "76. Lắng nghe tiếng chuông ngân vào hư không, lòng nhẹ nhõm như chưa từng lo âu.",
    "77. Trái tim rỗng rang là trái tim đong đầy tình yêu thương chân thật.",
    "78. Mọi hình tướng rồi sẽ tan hòa vào cái Không rộng lớn của vũ trụ.",
    "79. Khi không còn bám chấp vào có hay không, ta bước vào cảnh giới tự tại.",
    "80. Tĩnh lặng là ngôn ngữ nguyên sơ của vũ trụ. Hãy lắng nghe trong yên lặng.",
    "81. Như ánh trăng soi bóng xuống đáy hồ, hiện rõ mà không để lại vết sẹo trên mặt nước.",
    "82. Sự rỗng rang trong tâm hồn chính là chiếc cầu nối ta với vạn vật.",
    "83. Đừng tìm kiếm sự tĩnh lặng ở nơi nào xa xôi, nó đang có mặt ngay trong hơi thở này.",
    "84. Nhìn thấu Tánh Không để sống nhiệt thành mà không bám chấp.",
    "85. Bình an là khi tâm ta tĩnh lặng như mặt hồ không một gờn sóng.",
    "86. Hãy như khoảng trống trong chiếc bình, tạo nên giá trị cho chiếc bình.",
    "87. Khi mọi ý niệm phân biệt tan biến, thực tại hiện ra trong vẻ đẹp nguyên sơ.",
    "88. Tâm không phân biệt là tâm chan hòa cùng vạn vật.",
    "89. Đi qua muôn vàn bão bùng mà lòng vẫn giữ được sự bình yên trong trẻo.",
    "90. Hãy mỉm cười với mọi trải nghiệm, vì tất cả rồi cũng sẽ trôi qua.",
    "91. Tánh Không là nguồn gốc của mọi sự chữa lành và bình an.",
    "92. Đừng sợ hãi sự trống rỗng, đó chính là khoảng không cho ước mơ bay xa.",
    "93. Khi ta tĩnh lặng hoàn toàn, cả vũ trụ lắng nghe cùng ta.",
    "94. Sự trong trẻo của tâm hồn là tài sản quý giá nhất của con người.",
    "95. Hãy để những lo âu lắng xuống như phù sa đọng lại đáy sông trong.",
    "96. Trở về với Tánh Không là trở về với ngôi nhà bình yên nhất của tâm hồn.",
    "97. Sống nhẹ nhàng, thở dịu êm, yêu thương vô điều kiện.",
    "98. Mọi âm thanh đều phát xuất từ sự tĩnh lặng và rồi quay trở về với tĩnh lặng.",
    "99. Hãy là khoảng không bao la cho mọi bông hoa rực rỡ ngát hương.",
    "100. Nam Mô Bổn Sư Thích Ca Mâu Ni Phật — LIDO Meditation nguyện chúc bạn luôn an yên và tự tại trong từng phút giây."
]

def generate_ass_subtitles(quotes, output_ass_path, video_duration_sec=10800):
    num_quotes = len(quotes)
    duration_per_quote = video_duration_sec / num_quotes  # 108 seconds per quote for 3 hours
    
    ass_header = """[Script Info]
Title: 100 Quotes Vo Thuong Vo Nga Tanh Khong
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: MeditationQuote,Arial,36,&H00FFFFFF,&H000000FF,&H80000000,&H80000000,0,0,0,0,100,100,0,0,1,2,2,2,100,100,90,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    def format_time(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        cs = int((s - int(s)) * 100)
        return f"{h}:{m:02d}:{int(s):02d}.{cs:02d}"

    events = []
    for i, quote in enumerate(quotes):
        start_sec = i * duration_per_quote
        end_sec = (i + 1) * duration_per_quote
        
        start_str = format_time(start_sec)
        end_str = format_time(end_sec)
        
        # Format text with line wraps if long
        words = quote.split()
        if len(words) > 12:
            mid = len(words) // 2
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:])
            formatted_text = f"{line1}\\N{line2}"
        else:
            formatted_text = quote
            
        events.append(f"Dialogue: 0,{start_str},{end_str},MeditationQuote,,0,0,0,,{formatted_text}")

    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events))
    print(f"Generated ASS Subtitle File: {output_ass_path}")

def main():
    quotes_file = "data/quotes_100.json"
    ass_file = "data/quotes_100.ass"
    os.makedirs("data", exist_ok=True)
    
    with open(quotes_file, "w", encoding="utf-8") as f:
        json.dump(QUOTES_100, f, ensure_ascii=False, indent=2)
    print(f"Saved 100 Quotes JSON: {quotes_file}")
    
    generate_ass_subtitles(QUOTES_100, ass_file, video_duration_sec=10800)

if __name__ == "__main__":
    main()
